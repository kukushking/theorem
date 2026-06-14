"""The `Prover` interface — the swappable LLM backend.

Two implementations live in `provers/`:
  - `ClaudeProver`  — Claude Opus 4.8 via the Anthropic Console API
  - `LocalProver`   — DeepSeek-Prover-V2-7B served by Ollama

Adding a third (a different API, a different local model) is just a new file
implementing this interface.
"""
from abc import ABC, abstractmethod


class Prover(ABC):
    """Generate a Lean 4 proof body for a given theorem statement."""

    # subclasses set this to a short identifier used in logs / RESULTS.md
    name: str = "?"

    @abstractmethod
    def propose(self, theorem: str, prior_errors: list[str]) -> str:
        """Propose a proof for the theorem.

        Args:
            theorem: full theorem-statement up to (but not including) `:=`,
                     e.g. `"theorem t (n : Nat) : n + n = 2 * n"`.
            prior_errors: Lean error strings from previous failed attempts on
                          this same theorem (empty on the first attempt). The
                          prover can use them to avoid repeating mistakes.

        Returns:
            A Lean proof — either the bare body (`by omega`) or the full
            theorem with proof (`theorem ... := by omega`). The agent's
            `build_lean_code` normalises both into compilable Lean.
        """
        raise NotImplementedError
