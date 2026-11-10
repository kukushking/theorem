# Rung 5 — Coq (now "Rocq"): the second assistant

> This rung moves to **Coq** — the other major assistant, the one behind CompCert,
> the Four Color theorem, and Feit–Thompson — and it starts where an engineer
> starts: with a *program*. Three files, in order:
>
> 1. **`program.v`** — Coq as a programming language. Functions, running them,
>    unit tests. One new idea total: a unit test with `forall` in it.
> 2. **`basics.v`** — the logic phrasebook: rung 2's theorems re-proved, so you
>    feel what transfers from Lean (every concept) and what doesn't (the syntax).
> 3. **`verified.v`** *(optional)* — the industrial demo: insertion sort proven
>    correct against a spec. Read the *statements*; skip the proof bodies.

**Naming note, 2025:** Coq was officially renamed the **Rocq Prover** (version 9.0).
Binaries, package names, and new docs say `rocq`; thirty years of books, papers, and
Stack Overflow answers say Coq. You need both words. The canonical textbook is still
[Software Foundations](https://softwarefoundations.cis.upenn.edu/).

## Setup

```bash
brew install rocq          # ~1 min, Apple Silicon bottle
rocq compile program.v     # 1: programs + unit tests (watch Compute print answers)
rocq compile basics.v      # 2: the logic phrasebook
rocq compile verified.v    # 3 (optional): a verified program (insertion sort)
```

VS Code: install the **VsCoq** extension for the live goal view (the Lean infoview
experience; point it at the `vscoqtop` binary that ships with the brew install).

## How to make this stuff make sense

Two rules, and the first one is the whole game:

**1. Never read a proof script as text.** A `.v` file is a *transcript of an
interactive session* — like a chess scoresheet, the information isn't in the
moves, it's in the board after each move. The "board" is the goal panel in
VS Code. Put your cursor after a tactic, look at the goal, move down one line,
look again. Every fluent user works this way; nobody sight-reads tactics.
If a proof "makes very little sense", 90% of the time it's being read cold.

**2. You already know these concepts — only the names are new.**

| You know it as | Coq calls it |
|---|---|
| a function | `Definition` / `Fixpoint` |
| running the program | `Compute` |
| a unit test (`assertEqual`) | `Example ... Proof. reflexivity. Qed.` |
| property-based testing (QuickCheck), but exhaustive | a `Theorem` with `forall` |
| a loop invariant | `induction` |
| the constraint solver from rung 1 | `lia` / `nia` |
| the contract / interface | the statement between `:` and `.` |
| a skipped test (quietly booked as an axiom) | `Admitted.` |
| the CI gate that can't be bribed | the kernel, at `Qed.` |

The honest caveat: yes, it *is* another programming language, and the type
system is the deepest one in production use. But the learning path is not
"memorize the symbols" — it's "step through files in the IDE with the goal
panel open until the moves become obvious". Budget is measured in hours,
not months, for everything this rung contains.

## What's in `program.v` — start here

Zero logic symbols. `add` and a running sum, `Compute` to run them (the answers
print at compile time), `Example` unit tests the compiler refuses to skip, and
then the single conceptual step this whole field rests on: `add 2 3 = 5` checks
one input, `forall a b, add a b = add b a` is the same test with infinite
coverage. The showpiece is Gauss's formula `2 * sum_to n = n * (n + 1)` —
a property you cannot test exhaustively, proved by `induction`, which is just
a loop invariant wearing a gown. The last exercise is the most engineer-shaped
theorem in the repo: refactor `sum_to` to tail-recursive `sum_fast`, then
*prove the refactor changed nothing*.

## What's in `basics.v`

The same theorems as `02-lean-basics/`, in the same order — propositional logic,
computation, induction, a decision procedure — plus the one *deliberate* difference:

**The flip.** In Lean, `n + 0 = n` is true by definition and `0 + n = n` needs
induction. In Coq it's exactly reversed, because Coq's `+` recurses on its *first*
argument where Lean's recurses on the second. Same theorem, opposite "trivial"
direction. This is the cleanest demonstration anywhere of what "definitional
equality" means: *by definition* is a fact about how someone wrote a function,
not about mathematics.

The audit idea carries over too: Coq's `Print Assumptions` is Lean's
`#print axioms` — the file ends by running it, and the kernel answers
`Closed under the global context` (no axioms at all; core Coq doesn't even
need Lean's three).

## What's in `verified.v` — the industrial demo (optional)

**Reading advice: read the statements, skip the proof bodies.** The statements
(`sort_correct : sorted (sort l) /\ Permutation l (sort l)`) are the contract —
that's the 90% of the value, and they read like types. The proof bodies are the
part nobody sight-reads (rule 1 above); step through them in VS Code later, or
never. Every other file in this repo proves *mathematical statements*; this one
does what CompCert, Iris, and Fiat-Crypto do at industrial scale, on a toy:

1. **The program** — insertion sort, written as ordinary functional code. Nothing
   proof-flavored about it; it's the same `insert`/`sort` you'd write in OCaml.
2. **The specification** — what "correct" *means*, as kernel-checkable data:
   the output is **sorted** (an inductive predicate you define) **and** a
   **permutation** of the input (the standard library's `Permutation`).
3. **The proof** — one helper lemma per half, induction stitches them together,
   and `Print Assumptions sort_correct` answers `Closed under the global context`.

The load-bearing lesson is in the spec, not the proof. Each half alone is
**gameable**:

| Program | Sorted? | Permutation? |
|---|---|---|
| `fun l => []` | ✅ always | ❌ |
| `fun l => l`  | ❌ | ✅ always |
| `sort` | ✅ | ✅ |

Only the conjunction forces the program to actually sort — and the third exercise
has you *prove the cheating program satisfies half the spec*, so you experience
spec-gaming from the inside. The kernel checks that the proof matches the spec;
**nothing checks that the spec says what you meant**. That — not proving — is the
hard problem of software verification, and it's exactly where current LLM+FV
research says the bottleneck is.

Style note: `verified.v` is **extrinsic** verification — program first, proofs
about it second, connected by theorems. The **intrinsic** alternative gives
`sort` a *type* only sorted permutations inhabit, so an incorrect program won't
compile — the program *is* the proof (Curry–Howard, load-bearing). Elegant,
harder to engineer, and the direction some of the Lean tooling world is heading.

## The phrasebook

| Concept | Lean 4 | Coq |
|---|---|---|
| assume / introduce | `intro h` | `intros h.` |
| provide exact term | `exact hp` | `exact hp.` |
| case split | `cases h with ...` | `destruct h as [a \| b].` |
| build a conjunction | `⟨h1, h2⟩` | `split.` |
| induction | `induction n with ...` | `induction n as [\| k IH].` |
| rewrite | `rw [h]` | `rewrite h.` |
| by computation | `rfl` | `reflexivity.` |
| linear arithmetic | `omega` | `lia` |
| placeholder | `sorry` | `Admitted.` |
| the audit | `#print axioms foo` | `Print Assumptions foo.` |
| seal a proof | (whitespace) | `Qed.` |

Ten minutes with this table and rung 2's muscle memory ports straight across. That's
the lesson: the *ideas* — Curry–Howard, tactics, goal states, kernel checking,
decision procedures — are assistant-independent.

## Exercises

`Admitted.` holes at the bottom of *each* file. Replace each with a proof
ending in `Qed.`, recompile, and run `Print Assumptions` on your theorem to
confirm the kernel holds no IOUs.

The `program.v` set is the engineer's on-ramp: a unit test (one tactic), a
`forall` property (mimic `add_commutes`), and the tail-recursion refactor-safety
theorem (the helper lemma's statement is given; `induction` then follow the IH).
The `basics.v` three mirror rung 2's `sorry` exercises. The `verified.v` three
are the software-verification set — hints, mildest first:

1. `ex_sort_example` — the kernel can *run* programs; one tactic from the
   computation row of the phrasebook.
2. `ex_insert_length` — induction on `l`; in the cons case, `destruct (x <=? h)`
   *before* `simpl`, then the IH closes it.
3. `ex_cheat_is_sorted` — one constructor. The real exercise is the follow-up in
   the comment: try proving the *permutation* half for `cheat_sort` and watch it
   dead-end at `Permutation [1] []`.

## Why this rung matters for software verification

Mathematics may be moving to Lean, but **formal software verification still runs
substantially on Coq**: CompCert (the verified C compiler), VST (verified C against
real semantics), **Iris** (the separation-logic framework behind most modern
concurrency and Rust verification work), and Fiat-Crypto, whose verified
elliptic-curve code ships inside Chrome. If the conversation is "prove the *program*
correct" rather than "prove the *theorem*", this ecosystem is where most of the
installed base lives — with Lean's share growing (Cedar's authorization model and
the SampCert differential-privacy library are both verified in Lean). `verified.v`
is this world's "hello, world": insertion sort against a sorted-∧-permutation spec
is the opening move of Software Foundations volume 3 (*Verified Functional
Algorithms*), and volume 2 (*Programming Language Foundations*) is the on-ramp
from here to verifying programs with state, pointers, and loops.

## Why this rung matters for the LLM story

Every LLM-prover benchmark that matters today targets **Lean** (rung 4 and
[`../RESEARCH.md`](../RESEARCH.md)) — but that's a 2020s contingency, not a law of
nature. GPT-f targeted Metamath, early DeepMind work used Isabelle and HOL Light,
and CoqGym/Proverbot9001 built the first learned tactic predictors on Coq. If you
can read both ecosystems you can read the whole literature, and you'll recognize
when a "new" idea is an old one wearing the other syntax.

## References

- [Software Foundations](https://softwarefoundations.cis.upenn.edu/) — the Coq book
  (volume 1 covers everything this rung touches).
- [Rocq Prover](https://rocq-prover.org/) — official site, rename FAQ, install docs.
- [CoqHammer](https://coqhammer.github.io/) — the Coq hammer, if you want the
  rung-3 experience on this side of the fence.
- CompCert, the verified C compiler — the crown jewel of Coq software verification.
