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
class VerifyResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    has_sorry: bool = False
    raw: str = ""


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
        has_sorry = False
        # `messages` is the standard lean-interact response field; severity is
        # one of "error" / "warning" / "info"; the text lives in `data`.
        for m in getattr(response, "messages", []) or []:
            sev = getattr(m, "severity", "info")
            text = getattr(m, "data", str(m))
            if sev == "error":
                errors.append(text)
            if "sorry" in text.lower():
                has_sorry = True
        ok = not errors and not has_sorry
        return VerifyResult(ok=ok, errors=errors, has_sorry=has_sorry, raw=str(response))
