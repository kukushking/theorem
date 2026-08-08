# Automated Theorem Proving Bootcamp

> *I spent the tokens on it so you don't have to.*

A hands-on, build-first path into automated theorem proving (ATP) — from "what even
*is* this field" to running real provers on your own machine, with an eye on how modern
**LLMs** fit in. Everything here is something you can **run and test**, not just read.

It's organized as a 4-rung ladder. Do them in order; each is an hour or two.

| # | Rung | You'll run | Folder |
|---|------|-----------|--------|
| 1 | **SMT solving** — fully-automatic logic + arithmetic engines (the industrial workhorse) | `uv run 01-smt/examples.py` | [`01-smt/`](./01-smt) |
| 2 | **Lean 4 basics** — interactive proving; the language LLM provers target | `cd 02-lean-basics && lake build` | [`02-lean-basics/`](./02-lean-basics) |
| 3 | **Lean + Mathlib + a hammer** — proving against the 274K-theorem library, with one-button automation | `cd 03-lean-math && lake env lean LeanMath/Hammer.lean` | [`03-lean-math/`](./03-lean-math) |
| 4 | **Leverage an LLM** — an agent loop: LLM drafts a proof → Lean verifies → iterate on errors. Extended runs of this loop have landed merged proofs in Google DeepMind's formal-conjectures ([#4286](https://github.com/google-deepmind/formal-conjectures/pull/4286), [#4411](https://github.com/google-deepmind/formal-conjectures/pull/4411)) | `cd 04-llm-agent && uv run python agent.py --all --prover local` | [`04-llm-agent/`](./04-llm-agent) |

📖 **[`GETTING_STARTED.md`](./GETTING_STARTED.md)** — the detailed, do-it-yourself walkthrough.
🔬 **[`RESEARCH.md`](./RESEARCH.md)** — the field survey: classical ATP, SMT, hammers, the
LLM frontier (AlphaProof, DeepSeek-Prover, Seed-Prover, Hilbert, Aristotle…), benchmarks,
and ~50 source links.

---

## The one idea behind all of it

> A proof is something a machine can **check** cheaply and soundly — even when it was
> **found** by something unreliable (a search procedure, or an LLM). The checker is
> ground truth.

That's why this field is uniquely friendly to "build and test": you always get an
automatic, unfakeable pass/fail signal. The whole modern LLM-prover paradigm is just:
*let a model generate, let a kernel verify, loop.*

## Quick start

Tested on **macOS (Apple Silicon)**; Linux works with equivalent installs.

```bash
# 1. Prerequisites (one-time)
brew install z3                                            # SMT solver
curl -LsSf https://astral.sh/uv/install.sh | sh           # Python runner (for 01-smt/)
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh    # Lean toolchain manager
export PATH="$HOME/.elan/bin:$PATH"                        # add to ~/.zshrc to persist

# 2. Rung 1 — instant
uv run 01-smt/examples.py

# 3. Rung 2 — instant (core Lean, no Mathlib)
cd 02-lean-basics && lake build && cd ..

# 4. Rung 3 — first run downloads the prebuilt Mathlib cache (~7 GB)
cd 03-lean-math
lake exe cache get          # MUST run from inside 03-lean-math (see gotcha below)
lake build
lake env lean LeanMath/Hammer.lean   # no output = all the automation tactics work
cd ..

# 5. Rung 4 — LLM-driven Lean prover (see 04-llm-agent/README.md for Anthropic / Ollama setup)
brew install --cask ollama && open -a Ollama
ollama pull qwen2.5-coder:7b
cd 04-llm-agent && uv sync && uv run python agent.py --all --prover local
```

Install the VS Code **Lean 4** extension to watch proof goals update live as you type.
New to Lean? The browser-based [Natural Number Game](https://adam.math.hhu.de/#/g/leanprover-community/nng4)
is the best first hour.

> ⚠️ **Toolchain gotcha.** Always run `lake` from *inside* `03-lean-math/`. That folder's
> `lean-toolchain` pins `v4.30.0-rc2` to match Mathlib; from the parent folder Lean falls
> back to a different default and you get `incompatible header` errors on `.olean` files.

## Repo map

```
.
├── README.md             # you are here
├── GETTING_STARTED.md    # detailed walkthrough of the 4 rungs
├── RESEARCH.md           # the field: SOTA, frontier systems, benchmarks, sources
├── 01-smt/               # Rung 1 — Z3 / SMT examples + exercises
├── 02-lean-basics/       # Rung 2 — core-Lean proofs (no Mathlib, instant build)
├── 03-lean-math/         # Rung 3 — Lean + Mathlib workbench + HAMMER.md (cache not committed)
└── 04-llm-agent/         # Rung 4 — LLM-driven Lean prover (Anthropic API + Ollama)
```

The big build artifacts (`**/.lake/`, the multi-GB Mathlib cache, `.olean` files) are
**git-ignored** — a fresh clone rebuilds them with `lake exe cache get`.

## Field highlights (the TL;DR of `RESEARCH.md`)

- **Lean 4 is the center of gravity** for LLM theorem proving — nearly every state-of-the-art
  prover ships Lean checkpoints.
- The classic benchmark (**miniF2F**) is essentially **saturated (~99%)**; the frontier
  moved to **PutnamBench** and, in 2025–2026, to **agentic provers** (Apple/UCSD's *Hilbert*,
  Logical Intelligence's *Aleph*, ByteDance's *Seed-Prover 1.5*).
- At IMO 2025, three AIs hit **gold** — but only Harmonic's **Aristotle** produced
  *machine-checked* (formal Lean) proofs; the others wrote human-graded prose.
- **Combinatorics is everyone's weak spot.**
- You can do real work on a laptop: the cheapest strong setup is a frontier LLM as the
  brain + **local Lean as a free, infallible verifier** + an iterate-on-errors loop.

---

*Built as a guided dive with [Claude Code](https://claude.com/claude-code). Corrections
and PRs welcome.*
