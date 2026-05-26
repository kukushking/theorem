# SMT warm-up (Z3)

SMT = **S**atisfiability **M**odulo **T**heories: a SAT solver plus decision procedures
for theories (integers, reals, arrays, bitvectors, uninterpreted functions, ...). These
are the fully-automatic workhorses behind most program verification.

## Run

```bash
uv run 01-smt/examples.py     # 5 commented Python examples (uv auto-installs z3-solver)
z3 01-smt/01_basics.smt2      # find a model (sat)
z3 01-smt/02_prove.smt2       # prove by refutation (unsat)
```

## Files
- `examples.py` — constraint solving, proof-by-refutation, graph coloring,
  uninterpreted functions, quantifiers.
- `01_basics.smt2`, `02_prove.smt2` — the raw SMT-LIB v2 input language.
- `EXERCISES.md` — five puzzles to try yourself.

## The big idea
`F` is **valid** (a theorem) ⟺ `¬F` is **unsatisfiable**. So you "prove" `F` by asking
the solver to satisfy `¬F` and getting `unsat`. If it's `sat`, the model is a
**counterexample**. This refutation loop underlies essentially all automated proving.

## Where this goes next
SMT solvers are the *backends* that "hammers" (Sledgehammer, LeanHammer, CoqHammer) call
to discharge goals from interactive provers. Learning Z3 here pays off in Rung 3.

Docs: Z3 guide https://microsoft.github.io/z3guide/ · SMT-LIB https://smt-lib.org
