"""Local prover served by Ollama — same `Prover` interface as `ClaudeProver`.

Default model: **`qwen2.5-coder:7b`** (Q4, ~4.7 GB on disk).

Why qwen2.5-coder and not DeepSeek-Prover-V2-7B? We tried both on a 16 GB
Mac. The `mradermacher/DeepSeek-Prover-V2-7B-GGUF` quants (Q4 and Q5) produce
garbled prose with malformed LaTeX — likely a bad upload, not the underlying
model's fault. qwen2.5-coder isn't Lean-specialized, but at Q4 it follows
instructions cleanly and one-shots simple targets like `n + n = 2*n` with
`omega`. See README → "Local prover — quality gotchas" for the full story.

If you have 24 GB+ and want to swap in a real prover model, pass
`--model huggingface.co/mradermacher/DeepSeek-Prover-V2-7B-GGUF:Q6_K` (or
similar) and adjust the prompt.
"""
from __future__ import annotations

import re
from typing import Optional

import httpx

from prover import Prover


DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_HOST = "http://localhost:11434"


SYSTEM_PROMPT = """\
You are an expert Lean 4 theorem prover. Given a theorem statement, output ONLY \
the proof — the tactics that go after `:= by`, or the full `:= by …` block. \
Do NOT include the theorem statement itself. Do NOT use markdown fences (no ```). \
Do NOT include any commentary or explanation.

Mathlib is available. Use any of these tactics as appropriate:
- omega           — linear arithmetic over Nat/Int (a decision procedure)
- ring            — commutative-ring identities (e.g. (a+b)^2 = a^2 + 2*a*b + b^2)
- linarith        — linear arithmetic over ordered fields
- nlinarith       — some nonlinear arithmetic
- simp            — simplify by @[simp] lemmas
- aesop / tauto   — general proof search / propositional tautologies
- intro, exact, apply, rfl, rw, obtain — basic structural tactics

CRITICAL — write Lean 4, NOT Lean 3. Common Lean-3 idioms that DO NOT WORK:
- `and.intro` / `or.inl`   →  Lean 4 wants `And.intro` / `Or.inl` (capitalised).
- `and.comm` / `Or.symm`   →  Lean 4: `And.comm`, `Or.comm`, …
- `cases h with hp hq,`    →  Lean 4: `obtain ⟨hp, hq⟩ := h`  (or `let ⟨hp, hq⟩ := h`).
- `intro h, exact h`       →  Lean 4 separates tactics with `;` or newlines, never commas.
- Build an `And` with `⟨_, _⟩`; project with `h.1` / `h.2` (or `h.left` / `h.right`).

Worked example for `p ∧ q → q ∧ p`:
    := by intro h; exact ⟨h.2, h.1⟩

If a previous attempt failed, the user will show you the Lean compiler error — \
read it and try a different approach. Output just the proof, nothing else.
"""


_FENCE_RE = re.compile(r"^```[a-zA-Z0-9]*\s*\n?|\n?```\s*$")


def _build_user_message(theorem: str, prior_errors: list[str]) -> str:
    parts = [f"THEOREM:\n{theorem.strip()}"]
    if prior_errors:
        parts.append("\nPREVIOUS FAILED ATTEMPTS (with Lean compiler errors):")
        for i, err in enumerate(prior_errors, 1):
            first_lines = "\n".join(err.splitlines()[:4])[:400]
            parts.append(f"\nAttempt {i} error:\n{first_lines}")
    parts.append("\nPropose a Lean 4 proof.")
    return "\n".join(parts)


def _clean(text: str) -> str:
    """Strip any markdown fences and surrounding whitespace."""
    text = text.strip()
    # Strip a leading fence (with or without language tag)
    text = re.sub(r"^```[a-zA-Z0-9]*\s*\n", "", text)
    # Strip a trailing fence
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


class LocalProver(Prover):
    name = "local"

    def __init__(
        self,
        model: Optional[str] = None,
        host: str = DEFAULT_HOST,
        max_tokens: int = 512,
        temperature: float = 0.2,
        timeout: float = 240.0,
    ):
        self.model = model or DEFAULT_MODEL
        self.host = host.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature
        # Local inference on a fanless Air can throttle; 4-minute timeout is safe.
        self.client = httpx.Client(timeout=timeout)

    def propose(self, theorem: str, prior_errors: list[str]) -> str:
        user_msg = _build_user_message(theorem, prior_errors)
        try:
            r = self.client.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
            )
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"Could not reach Ollama at {self.host}. "
                f"Is the Ollama app running? ({e})"
            ) from e

        if r.status_code != 200:
            raise RuntimeError(f"Ollama returned {r.status_code}: {r.text[:300]}")

        body = r.json()
        content = body.get("message", {}).get("content", "")

        # Throughput stats — useful for spotting cold-cache vs warm runs.
        eval_count = body.get("eval_count")
        eval_duration_ns = body.get("eval_duration")
        if eval_count and eval_duration_ns:
            tok_per_s = eval_count / (eval_duration_ns / 1e9)
            print(f"  [local] {eval_count} tok @ {tok_per_s:.1f} tok/s")

        return _clean(content)

    def __del__(self):
        try:
            self.client.close()
        except Exception:
            pass
