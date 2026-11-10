# Getting started — fundamentals first

A hands-on path into automated theorem proving. Each rung has something you can
**run and test today**. Do them in order; each takes an hour or two.

For the field overview, frontier systems, and ~50 source links, see [`RESEARCH.md`](./RESEARCH.md).

> **The one idea that ties it all together:** a proof is something a machine can
> *check* cheaply and soundly, even when it was *found* by something unreliable (a
> search procedure or an LLM). The checker is the ground truth. Everything below is a
> different way of producing things for a checker to verify.

---

## What's installed (verified on this machine)

| Tool | Version | Check it |
|---|---|---|
| Z3 (SMT solver) | 4.15.4 | `z3 --version` |
| `uv` (Python runner) | present | `uv --version` |
| Lean 4 + Lake | 4.29.1 default; 4.30.0-rc2 for Mathlib | `~/.elan/bin/lean --version` |
| Mathlib | v4.30.0-rc2 (in `03-lean-math/`) | see Rung 3 |

`elan` lives in `~/.elan/bin`. If `lean`/`lake` aren't found, add that to your PATH:
```bash
echo 'export PATH="$HOME/.elan/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

---

## Rung 1 — SMT solving (the fastest win)  ·  `01-smt/`

SMT solvers are *fully automatic* engines for logic + arithmetic. They're the most
industrially useful thing here (Dafny, F*, Rust verifiers, etc. all sit on Z3/cvc5).

```bash
uv run 01-smt/examples.py        # 5 worked examples; uv auto-installs z3-solver
z3 01-smt/01_basics.smt2         # the raw SMT-LIB language
z3 01-smt/02_prove.smt2          # proving by refutation -> 'unsat'
```
Then do [`01-smt/EXERCISES.md`](./01-smt/EXERCISES.md). Key takeaway: **a theorem is valid
iff the negation is unsatisfiable** — that refutation trick is the heart of automation.

## Rung 2 — Lean 4 basics (interactive proving)  ·  `02-lean-basics/`

Lean is the proof assistant that LLM provers overwhelmingly target. Start here:

1. **Browser, no install:** play the [Natural Number Game](https://adam.math.hhu.de/#/g/leanprover-community/nng4)
   — the best on-ramp to Lean tactics. Then skim [Mathematics in Lean](https://leanprover-community.github.io/mathematics_in_lean/).
2. **Locally:** open the `02-lean-basics/` folder in VS Code (install the **Lean 4**
   extension). Open `LeanBasics/Basic.lean`, put your cursor in a proof, and watch the
   goal state in the infoview. Or from the terminal:
   ```bash
   cd 02-lean-basics && lake build      # compiles = all proofs check
   ```
3. The file ends with three `sorry` exercises — replace each `sorry` with a real proof
   and rebuild. A red squiggle / build error means it's wrong; that pass/fail signal is
   exactly what an automated prover loops on.

## Rung 3 — Lean + Mathlib + a "hammer"  ·  `03-lean-math/`

Mathlib (~274K theorems) is the library real proving happens against. The project in
`03-lean-math/` already has it.

```bash
cd 03-lean-math                                # IMPORTANT: run from inside the project
lake env lean LeanMath/Smoke.lean              # should print nothing = Mathlib works
```
> ⚠️ **Toolchain gotcha (we hit this):** always run `lake` from *inside* `03-lean-math/`.
> That folder's `lean-toolchain` file pins `v4.30.0-rc2` to match Mathlib; from the
> parent folder elan falls back to the default `v4.29.1` and you get
> `incompatible header` errors on `.olean` files.

**The "hammer" — classical automation under one tactic.** Mathlib already ships the
building blocks; try them in `LeanMath/Hammer.lean`:
- `exact?` / `apply?` — search the whole library for a lemma that closes/advances the
  goal (this *is* premise selection, interactively).
- `aesop` — general-purpose proof search.
- `omega`, `linarith`, `nlinarith`, `polyrith`, `ring` — decision procedures.

For a *real* hammer (premise selection → translate to FOL/SMT → external solver →
reconstruct), see [`HAMMER.md`](./03-lean-math/HAMMER.md): LeanHammer's `by hammer`,
or Isabelle's `sledgehammer`.

## Rung 4 — Leverage an LLM (where you're headed)

Once Rungs 1–3 feel comfortable, the modern move is an **agent loop**: an LLM proposes
a Lean proof → Lean verifies it → feed compiler errors back → retry. That's exactly
what the bleeding-edge systems (Hilbert, the "Minimal Agent" paper) do, and it's
solo-achievable on your Mac. The verifier you'll call is the same `03-lean-math` project
(programmatically, via `pip install lean-interact`). See `RESEARCH.md` §6 for the build
ladder and the [Minimal Agent paper](https://arxiv.org/abs/2602.24273) to copy from.

## Rung 5 — Coq (Rocq): the second assistant

Once the Lean rungs are done, spend an hour or two in **Coq** (renamed the **Rocq
Prover** in 2025): `brew install rocq`, then `cd 05-coq` and take the three files
in order. One reading rule first, from the rung's README: **never read a proof
script as text** — it's a transcript of an interactive session, and the
information lives in the goal panel (VS Code + VsCoq), not in the tactic names.

**Part 1 — `program.v`** is Coq as a programming language, no logic symbols:
define `add` and a running sum, run them with `Compute` (the answers print at
compile time), write unit tests the compiler refuses to skip, and meet the one
new idea — a unit test with `forall` in it is a theorem, property-based testing
with infinite coverage. The closing exercise is the most engineer-shaped theorem
in the repo: refactor to tail-recursion and *prove the refactor changed nothing*.

**Part 2 — `basics.v`** re-proves rung 2's theorems. The point is transfer — every
concept (Curry–Howard, tactics, goal states, kernel audits, decision procedures)
carries across assistants; only the syntax changes. The rung's README has a
Lean↔Coq phrasebook, and `basics.v` demonstrates the cleanest "definitional
equality" lesson in the repo: which of `n + 0 = n` / `0 + n = n` is trivial
*flips* between the two assistants.

**Part 3 — `verified.v`** *(optional)* is the industrial demo: **verify a
program**, the way CompCert and Fiat-Crypto do at scale. Insertion sort, a
specification (*output is sorted* ∧ *output is a permutation of the input*), and
a kernel-checked proof that the program meets it. Read the *statements* and skip
the proof bodies. The teaching core is the spec itself: each half alone is
gameable (`fun l => []` is always sorted; `fun l => l` is always a permutation),
and the exercises make you prove the cheating program satisfies half the spec,
so you feel why *writing specs that can't be gamed* — not proving — is the hard
problem of software verification.

---

## Layout

```
theorem/
├── RESEARCH.md           # the field: SOTA, frontier systems, benchmarks, sources
├── GETTING_STARTED.md    # this file
├── 01-smt/               # Rung 1: Z3 examples + exercises
├── 02-lean-basics/       # Rung 2: core-Lean proofs (no Mathlib, instant build)
├── 03-lean-math/         # Rung 3: Lean + Mathlib project + HAMMER.md (the real workbench)
├── 04-llm-agent/         # Rung 4: the LLM agent loop (Anthropic API + Ollama)
└── 05-coq/               # Rung 5: Coq/Rocq — second assistant + a verified program
```
