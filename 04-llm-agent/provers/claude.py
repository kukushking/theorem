"""Claude (Anthropic Console first-party API) — the frontier-API prover.

Uses the official Anthropic SDK with prompt caching on the static system prompt,
so retries pay ~0.1× the system prompt's input cost instead of full price.

Default model: `claude-opus-4-8` (current frontier Opus per the Anthropic models
catalog). Pass `--model` to pin a different one.

Knob notes:
  - Thinking: adaptive is the only on-mode for Opus 4.7+ (fixed `budget_tokens`
    is removed). We default `thinking: disabled` because on hard targets like
    the Lambert series identity, adaptive thinking filled the entire
    `max_tokens` budget with hidden reasoning and emitted zero text blocks
    (`stop_reason=max_tokens`). Disabling forces the model to commit to an
    answer directly — shallower reasoning, but shallow-and-emitted beats
    deep-and-empty.
  - Effort: `medium` — strong reasoning without paying max-effort prices on
    easy targets.
  - `max_tokens=32768` — comfortably above any sane Lean proof and leaves room
    for thinking blocks. Streaming required by the SDK above ~16K to avoid
    HTTP timeouts.
"""
from __future__ import annotations

import re
from typing import Optional

from anthropic import Anthropic

from prover import Prover


DEFAULT_MODEL = "claude-opus-4-8"


# STATIC across every attempt — this is exactly what `cache_control` wants.
# Anything that changes per attempt (the theorem, prior errors) goes in the user message.
SYSTEM_PROMPT = """\
You are an expert Lean 4 theorem prover.

You will receive:
1. A Lean 4 theorem statement (everything up to but excluding `:=`).
2. Optionally, a list of previous failed proof attempts with the Lean compiler errors they produced.

Your job is to propose a proof that closes the goal.

OUTPUT RULES (read carefully — the verifier compiles your output as raw Lean 4):
- Return ONLY the Lean proof. NO markdown fences. NO commentary. NO explanation.
- You may return either:
  (a) The bare proof body, starting with `by`, e.g.
        by omega
        by intro h; exact h.left
        by intro h; rcases h with ⟨ha, hb⟩; exact ⟨hb, ha⟩
  (b) The complete theorem with proof, starting with `theorem`/`example`/`lemma`, e.g.
        theorem foo (n : Nat) : n + n = 2 * n := by omega

Mathlib is available — use its tactics freely:
    omega           linear nat/int arithmetic (decision procedure)
    linarith        linear arithmetic over ordered fields
    nlinarith       some nonlinear arithmetic
    ring            commutative ring identities (e.g. (a+b)^2 = a^2+2ab+b^2)
    aesop           general-purpose proof search
    simp            simplification by lemmas tagged @[simp]
    exact?, apply?  library search (these are interactive — don't return them, but think with them)

If a previous attempt failed: read the compiler error and try a fundamentally different approach.
Don't just permute the same tactics — Lean's error message tells you *why* it failed; use that.

Return only the proof — nothing else.
"""


_FENCE_RE = re.compile(r"\s*```\s*$")


def _strip_fences(text: str) -> str:
    """If the model wrapped its output in ```lean ... ```, strip the fences."""
    text = text.strip()
    if not text.startswith("```"):
        return text
    # Drop the opening fence + optional language tag (everything up to the first newline).
    nl = text.find("\n")
    if nl == -1:
        return text
    text = text[nl + 1 :]
    # Drop the trailing fence.
    text = _FENCE_RE.sub("", text)
    return text.strip()


class ClaudeProver(Prover):
    name = "claude"

    def __init__(
        self,
        model: Optional[str] = None,
        max_tokens: int = 32768,
    ):
        self.max_tokens = max_tokens
        # Reads ANTHROPIC_API_KEY from env automatically.
        self.client = Anthropic()
        self.model = model or DEFAULT_MODEL

    def propose(self, theorem: str, prior_errors: list[str]) -> str:
        # Streaming is required by the SDK for max_tokens > ~16K to avoid HTTP
        # request timeouts. We don't need to handle individual stream events
        # because we only want the final concatenated text — `get_final_message()`
        # gives us the Message object as if we'd called `messages.create()`.
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            # Opus 4.7/4.8 specifics: adaptive thinking is the *only* on-mode;
            # `budget_tokens` and sampling params (temperature/top_p/top_k) return 400.
            # NOTE: thinking disabled. On Opus 4.8 with adaptive thinking, hard
            # targets like the Lambert series identity caused the model to fill
            # the entire `max_tokens` budget with thinking and never emit a text
            # block — `stop_reason=max_tokens`, zero usable output. Diagnostic
            # confirmed via direct API probe: 1789 thinking tokens / 0 text tokens
            # at max_tokens=4096 even on effort=medium. Disabling thinking forces
            # the model to commit to an answer directly. The trade-off: shallower
            # reasoning. Worth it because shallow-but-emitted beats deep-and-empty.
            thinking={"type": "disabled"},
            output_config={"effort": "medium"},
            # System prompt is identical every call — cache it once, read it cheap thereafter.
            # Note: Opus 4.7/4.8's min cacheable prefix is 4096 tokens; our system
            # prompt is ~750 so the cache silently won't fire. We keep `cache_control`
            # in case the prompt grows past 4096, and so it does fire on smaller models.
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": self._build_user_message(theorem, prior_errors)}],
        ) as stream:
            response = stream.get_final_message()

        # Surface cache hit rate so we can confirm caching is actually working.
        u = response.usage
        cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
        cache_write = getattr(u, "cache_creation_input_tokens", 0) or 0
        print(
            f"  [claude/{self.model}] tokens: input={u.input_tokens} "
            f"cache_read={cache_read} cache_write={cache_write} output={u.output_tokens}"
        )

        # Concatenate any text blocks (skip thinking blocks — those are reasoning, not the answer).
        proof_text = "".join(block.text for block in response.content if block.type == "text")
        return _strip_fences(proof_text)

    @staticmethod
    def _build_user_message(theorem: str, prior_errors: list[str]) -> str:
        parts = [f"THEOREM:\n{theorem.strip()}"]
        if prior_errors:
            parts.append("\n\nPREVIOUS FAILED ATTEMPTS (with Lean compiler errors):")
            for i, err in enumerate(prior_errors, 1):
                # Truncate massive error traces (some Lean errors dump huge expected/got types).
                trimmed = err if len(err) < 4000 else err[:4000] + "\n…[truncated]"
                parts.append(f"\nAttempt {i} error:\n{trimmed}")
        parts.append("\n\nPropose a Lean 4 proof that closes the goal.")
        return "".join(parts)
