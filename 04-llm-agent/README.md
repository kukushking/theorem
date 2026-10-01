# Rung 4 — Leverage an LLM (the agent loop)

> **The bootcamp's capstone.** Use an LLM to draft Lean 4 proofs, let Lean verify them,
> iterate on the compiler errors. Empirical, hands-on, and the truest test of where
> LLM-based theorem proving actually sits today.

## Field results: proofs merged into formal-conjectures

An extended, research-grade variant of this rung's loop has produced kernel-verified
proofs merged into Google DeepMind's
[formal-conjectures](https://github.com/google-deepmind/formal-conjectures):

> **Precision note:** what ships in this directory is the *minimal teaching loop* —
> deliberately small, meant to be read and rebuilt. The proofs below came from a
> research harness that grew out of it (full-file context, a Lean-idiom hint system,
> a goal-state repair loop, `#print axioms` auditing, per-run prompt provenance).
> That harness is **not yet in this repo**; publishing it, with its benchmark logs,
> is planned. Until then: the results are real and checkable via the PRs, but you
> cannot reproduce them with the code here alone.

- **[PR #4286](https://github.com/google-deepmind/formal-conjectures/pull/4286)** —
  the **Lambert series identity** (Erdős Problem 1049's textbook lemma; June 2026, +195/−1):
  for rational $|t| > 1$,
  $$\sum_{n=1}^{\infty} \frac{1}{t^n - 1} = \sum_{n=1}^{\infty} \frac{\tau(n)}{t^n},
  \qquad \tau(n) = \#\{d : d \mid n\}.$$
  Driven by Opus 4.8: the model produced ~95% of the proof structure, a human closed the
  remaining ~5% (a hallucinated lemma name, one missed case analysis).
- **[PR #4411](https://github.com/google-deepmind/formal-conjectures/pull/4411)** —
  `possible_f_values_BddAbove` (Erdős Problem 92 sanity check; July 2026, +13/−6). The
  problem concerns
  $$f(n) = \max\{\,k : \exists\, A \subset \mathbb{R}^2,\ |A| = n,\ \forall x \in A\ \text{at least } k \text{ points of } A \text{ are equidistant from } x\,\};$$
  the proof shows every point of an $n$-point set has at most $n$ equidistant companions,
  so the achievable $k$ are bounded and $f(n)$ is a well-defined supremum. Driven by Claude Fable 5:
  **closed on attempt 1 with no target-specific hints** and merged with only reviewer
  style golf — no human proof repair at all.
- A third proof (Hadamard's 12×12 matrix is a Hadamard matrix: entries $\pm 1$ and
  $|\det| = 12^6$) was closed by the harness on attempt 1 — then superseded before merge
  by another contributor's independent proof of the same `sorry`
  ([#6037](https://github.com/google-deepmind/formal-conjectures/pull/6037)); in a repo
  this active, speed matters.

Every claim above is checkable: each PR's axiom audit shows only `propext`,
`Classical.choice`, `Quot.sound` — no `sorryAx`, no user axioms.

Two lessons generalize. First, the agent loop's ceiling isn't structural reasoning
but **leaf-level tactic iteration** — a 5-minute human pass over a "failed" run often
converts it into a closure. Second, and more surprising: **the scaffold can be the
bottleneck, not the model.** The Hadamard proof failed 0/6 in the loop until the
harness learned to retry verification under a raised `maxHeartbeats` budget — after
which the model's *first attempt* turned out to have been correct all along. Measure
your harness before blaming your model.

## Architecture: one Lean verifier, swappable provers

```
                  ┌────────────────────┐
   target  ──►    │  Prover (LLM)      │   ──► proof body (str)
   + errors       └────────────────────┘
                            │
                            ▼
   ┌─────────────────────────────────────────────┐
   │  Verifier  (Lean kernel via lean-interact)  │
   └─────────────────────────────────────────────┘
                            │
                            ▼
                  ok / errors / sorry?   ──► loop with errors as context
```

Two provers, same `Prover` interface:
- **`ClaudeProver`** — Claude **Opus 4.8** via the Anthropic Console API. With prompt caching on the system prompt.
- **`LocalProver`** — defaults to **`qwen2.5-coder:7b`** (Q4) via Ollama. *Not* a Lean-specialised model, but it actually works at 4-bit on 16 GB. We tried `DeepSeek-Prover-V2-7B` first and discovered the available GGUF uploads are broken at low precision — see [`RESULTS.md`](./RESULTS.md) and the "Local prover — quality gotchas" section below.

The verifier runs against the **`03-lean-math/`** project (already has Mathlib) — no second 7 GB download.

## Setup

### 1. Python deps
```bash
cd 04-llm-agent
uv sync                    # installs lean-interact, anthropic, httpx
```

### 2. Anthropic Console (Claude prover)

You'll need:
- **Anthropic API key** — set `ANTHROPIC_API_KEY` in your environment. Sign up at https://console.anthropic.com/ and create a key under *API Keys*.
- **Model access** for `claude-opus-4-8` (the current frontier Opus) — first-party Anthropic has all current models available by default; nothing to request.

That's it. The SDK reads `ANTHROPIC_API_KEY` from the environment automatically, picks the default model, and you're running.

### 3. Ollama (Local prover)

```bash
# IMPORTANT: install the cask, not the formula. The brew formula's `llama-server`
# bundling is broken (Ollama returns "llama-server binary not found" at runtime).
brew install --cask ollama
open -a Ollama                              # starts the daemon on :11434

# Default model (works at Q4 on 16 GB Macs):
ollama pull qwen2.5-coder:7b                # ~4.7 GB

# Optional: specialist prover model. The mradermacher GGUF Q4/Q5 are
# garbled — only useful at Q6_K+ on 24 GB+. If you have the RAM:
# ollama pull huggingface.co/mradermacher/DeepSeek-Prover-V2-7B-GGUF:Q6_K
```

> **16 GB Mac note.** qwen2.5-coder at Q4 uses ~6 GB working RAM. Close heavy apps (browser tabs, Docker) during a run. The Air has no fan, so sustained batch runs will thermal-throttle after ~30 s — fine for single-target attempts.

### 4. Lean verifier

Nothing to install — the verifier points at your existing `03-lean-math/` project. Confirm it builds first:
```bash
cd ../03-lean-math && lake build && cd -
```

## Local prover — quality gotchas (16 GB Mac)

What we found running this on 16 GB Apple Silicon. Full empirical log in
[`RESULTS.md`](./RESULTS.md); summary here:

- **The publicly-available GGUFs of `DeepSeek-Prover-V2-7B` are broken at
  low precision.** Both Q4_K_M and Q5_K_M from `mradermacher`'s repo
  produced garbled prose (malformed LaTeX, invalid Lean tokens, no
  parseable proof). Same failure in raw completion mode and chat mode —
  it's a bad upload, not a chat-template issue. `bartowski`'s repo is
  gated/restricted.
- **A general-purpose code model beat the specialist at Q4.**
  `qwen2.5-coder:7b` at Q4 solved 2 / 3 easy targets in 35 seconds end-to-
  end (`by ring` one-shot for both arithmetic targets). It's *not* a Lean
  prover — but it follows instructions cleanly and reaches for the right
  Mathlib tactic with the right prompt.
- **The single recurring failure is Lean 3 syntax bleed-through.**
  qwen2.5-coder's training data is dominated by Lean 3 code from GitHub,
  so it emits `cases h with hp hq`, `and.intro`, `rw [and.comm]` —
  syntactically valid Lean 3, invalid Lean 4. The error feedback loop
  doesn't break it out, because Lean 4 errors say "unknown tactic" not
  "you're writing Lean 3". Adding a Lean-4-disambiguation clause to the
  system prompt is the obvious next move.
- **TL;DR for hardware:** 16 GB — use `qwen2.5-coder:7b` at Q4 and accept
  the Lean-4 syntax friction. 24 GB+ — try `DeepSeek-Prover-V2-7B-GGUF` at
  Q6_K, which is where the prover models start to behave like the paper
  claims. 32 GB+ — Q8 of the specialist, or the full-precision HF model
  via `transformers` (skip Ollama entirely).

This is exactly the kind of SOTA-limits lesson Rung 4 is meant to surface.
Log your own runs in [`RESULTS.md`](./RESULTS.md) — it's the deliverable.

## Run

```bash
# Single target, Claude
uv run python agent.py --target add_self_eq_two_mul --prover claude

# Single target, local
uv run python agent.py --target add_self_eq_two_mul --prover local

# All targets, both provers, log results
uv run python agent.py --all --prover claude
uv run python agent.py --all --prover local
```

## Files

```
04-llm-agent/
├── README.md           # this file
├── pyproject.toml      # uv project: lean-interact, anthropic, httpx
├── agent.py            # the loop: prover → Lean → retry on errors
├── prover.py           # Prover ABC — the swappable interface
├── verifier.py         # lean-interact wrapper (compiles a Lean snippet, returns errors)
├── targets.py          # the 3 easy hand-rolled theorems
├── provers/
│   ├── claude.py       # Claude via the Anthropic Console API + prompt caching
│   └── local.py        # DeepSeek-Prover-V2-7B via Ollama HTTP
└── RESULTS.md          # log of prover × target outcomes
```

## What you're meant to learn

- **The kernel makes generation safe.** The LLM hallucinates; Lean catches every false claim.
- **Whole-proof generation in action** — the dominant SOTA paradigm.
- **Where SOTA actually is** today — algebra falls easily, combinatorics breaks both provers, anything resembling open math is hopeless.
- **The agent loop is the unit of work** — propose, verify, feed errors back, retry.
- **Prompt caching matters.** The system prompt is static; every retry pays ~0.1× input cost on it thanks to `cache_control`. Confirm via the `cache_read=` line in the run log.

## References

- *A Minimal Agent for Automated Theorem Proving* (Requena et al., ICML 2026, arXiv:2602.24273) — the canonical reference for this rung.
- `lean-interact` — https://github.com/augustepoiroux/LeanInteract
- DeepSeek-Prover-V2 — https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-7B
- Field survey in [`../RESEARCH.md`](../RESEARCH.md).
