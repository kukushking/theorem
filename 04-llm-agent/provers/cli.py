"""Claude Code CLI prover — rides the user's Claude subscription.

Shells out to `claude -p` (headless one-shot mode) instead of calling the
Anthropic API with a Console key. Useful when the Console credit balance is
empty: subscription auth has no per-token billing.

Trade-offs vs `ClaudeProver` (the SDK path):
  - subscription rate windows cap sustained runs (fine for 6-attempt targets)
  - no prompt caching, no explicit max_tokens/effort control
  - no token accounting in the logs (the CLI doesn't report usage)
Keep the SDK prover as the primary; this is the fallback.
"""
from __future__ import annotations

import subprocess

from prover import Prover
from provers.claude import SYSTEM_PROMPT, _strip_fences


class CLIProver(Prover):
    name = "claude-cli"

    def __init__(self, model: str | None = None, timeout: float = 1800.0):
        self.model = model or "claude-fable-5"
        self.timeout = timeout

    def propose(self, theorem: str, prior_errors: list[str]) -> str:
        prompt = self._build_prompt(theorem, prior_errors)
        cmd = [
            "claude", "-p",
            "--model", self.model,
            # the harness prompt is self-contained; don't let the CLI wander
            # the repo with tools — text in, text out.
            "--tools", "",
            "--no-session-persistence",
        ]
        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True, timeout=self.timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:300]}")
        print(f"  [{self.name}/{self.model}] (subscription — no token accounting)")
        return _strip_fences(proc.stdout.strip())

    @staticmethod
    def _build_prompt(theorem: str, prior_errors: list[str]) -> str:
        # `claude -p` has no separate system-prompt channel in this harness's
        # usage; prepend it. Same content the SDK path sends.
        parts = [SYSTEM_PROMPT, f"\n\nTHEOREM:\n{theorem.strip()}"]
        if prior_errors:
            parts.append("\n\nPREVIOUS FAILED ATTEMPTS (with Lean compiler errors):")
            for i, err in enumerate(prior_errors, 1):
                trimmed = err if len(err) < 4000 else err[:4000] + "\n…[truncated]"
                parts.append(f"\nAttempt {i} error:\n{trimmed}")
        parts.append("\n\nPropose a Lean 4 proof that closes the goal.")
        return "".join(parts)
