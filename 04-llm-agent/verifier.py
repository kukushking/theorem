"""Lean verifier — wraps `lean-interact` against the 03-lean-math project.

We submit the prover's proof (with the right imports + theorem header) as a
single Lean snippet, then check the REPL's response for errors and lingering
`sorry`s. A proof "passes" only if both are clean.

Implementation notes (gleaned by introspection of lean-interact ≥0.11):
- `LocalProject(directory=...)` is the project wrapper; pass it to `LeanREPLConfig(project=...)`.
- `lake` must be on PATH for subprocesses; we prepend `~/.elan/bin` defensively
  because `uv run python` doesn't always inherit the interactive shell's PATH.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from lean_interact import Command, LeanREPLConfig, LeanServer, LocalProject


# Ensure elan's `lake`/`lean` are on PATH for any subprocess lean-interact spawns.
_ELAN_BIN = Path.home() / ".elan" / "bin"
if _ELAN_BIN.is_dir() and str(_ELAN_BIN) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_ELAN_BIN}{os.pathsep}{os.environ.get('PATH', '')}"


def _resolve_lake() -> str:
    """Find `lake` — prefer PATH, fall back to elan's default location."""
    found = shutil.which("lake")
    if found:
        return found
    elan_lake = _ELAN_BIN / "lake"
    if elan_lake.exists():
        return str(elan_lake)
    raise FileNotFoundError(
        "Could not find `lake` on PATH or at ~/.elan/bin/lake. "
        "Is Lean installed via elan?"
    )


@dataclass
class SorryGoal:
    """A `sorry` hole reported by the REPL: where it is and what goal it guards."""
    goal: str
    line: int | None = None       # 1-based, relative to the submitted snippet
    column: int | None = None
    end_line: int | None = None
    end_column: int | None = None


@dataclass
class ErrorAt:
    """An error message with its position (when the REPL provides one)."""
    text: str
    line: int | None = None       # 1-based, relative to the submitted snippet
    column: int | None = None


@dataclass
class VerifyResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    has_sorry: bool = False
    raw: str = ""
    # Structured views (added for the goal-state repair loop):
    sorries: list[SorryGoal] = field(default_factory=list)
    errors_at: list[ErrorAt] = field(default_factory=list)


class Verifier:
    """One long-lived Lean server pointed at a project (so Mathlib stays loaded).

    The first `verify()` call pays the Mathlib-loading cost (~20 s); subsequent
    calls are fast. Reuse the same instance across attempts and targets.
    """

    def __init__(self, project_dir: Path):
        project_dir = project_dir.resolve()
        if not (project_dir / "lean-toolchain").exists():
            raise FileNotFoundError(
                f"{project_dir} is not a Lean project (no lean-toolchain). "
                f"Point this at your 03-lean-math/ folder."
            )
        lake = _resolve_lake()
        # `auto_build=True` (default) does an incremental lake build of the project.
        # That's a no-op when 03-lean-math/.lake is already populated, which it is.
        project = LocalProject(directory=str(project_dir), lake_path=lake)
        config = LeanREPLConfig(project=project, lake_path=lake)
        self.server = LeanServer(config)
        self.project_dir = project_dir

    def verify(self, lean_code: str) -> VerifyResult:
        """Submit `lean_code` as a single command and report the outcome.

        ok == True  ⇔  no error messages AND no `sorry` left in the proof.
        """
        response = self.server.run(Command(cmd=lean_code))
        errors: list[str] = []
        errors_at: list[ErrorAt] = []
        has_sorry = False
        # `messages` is the standard lean-interact response field; severity is
        # one of "error" / "warning" / "info"; the text lives in `data`.
        for m in getattr(response, "messages", []) or []:
            sev = getattr(m, "severity", "info")
            text = getattr(m, "data", str(m))
            if sev == "error":
                errors.append(text)
                # NB: this lean-interact version populates `end_pos` but leaves
                # `pos` as None on messages — fall back accordingly.
                where = _pos_fields(m, "pos") or _pos_fields(m, "end_pos")
                errors_at.append(ErrorAt(text=text, **where))
            if "sorry" in text.lower():
                has_sorry = True
        # `sorries` carries each hole's goal state — the raw material for the
        # repair loop. Field shapes vary a little across lean-interact versions,
        # so read defensively.
        sorries: list[SorryGoal] = []
        for s in getattr(response, "sorries", []) or []:
            goal = getattr(s, "goal", None)
            if goal is None:
                goals = getattr(s, "goals", None)
                goal = "\n".join(goals) if goals else str(s)
            start = _pos_fields(s, "start_pos") or _pos_fields(s, "pos")
            end = _pos_fields(s, "end_pos")
            sorries.append(SorryGoal(
                goal=str(goal),
                line=start.get("line"), column=start.get("column"),
                end_line=end.get("line"), end_column=end.get("column"),
            ))
        ok = not errors and not has_sorry
        return VerifyResult(ok=ok, errors=errors, has_sorry=has_sorry,
                            raw=str(response), sorries=sorries, errors_at=errors_at)


def _pos_fields(obj, attr: str) -> dict:
    """Extract {line, column} from a lean-interact position attribute, tolerantly."""
    pos = getattr(obj, attr, None)
    if pos is None:
        return {}
    line = getattr(pos, "line", None)
    column = getattr(pos, "column", None)
    if line is None and isinstance(pos, dict):
        line, column = pos.get("line"), pos.get("column")
    out = {}
    if line is not None:
        out["line"] = line
    if column is not None:
        out["column"] = column
    return out
