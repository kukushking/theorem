# SMT exercises

Work these in `01-smt/exercises.py` (copy a worked function from `examples.py` and adapt) or as `.smt2` files.
Each one reinforces the "validity = unsat of the negation" idea.

1. **Prove** that for all integers `x, y`: `(x + y) * (x + y) == x*x + 2*x*y + y*y`.
   (Assert the negation; expect `unsat`.)

2. **Disprove** `x*x == 2` over the integers (no integer square root of 2), then
   switch `x` to a `Real` and show it becomes satisfiable.

3. **Pigeonhole**: place 4 pigeons into 3 holes with no two pigeons in the same
   hole. Model `hole_i in {0,1,2}` for `i in 0..3` and require all `Distinct`.
   It should be `unsat` — that *is* the pigeonhole principle for these numbers.

4. **A logic puzzle**: 3 people each either always lie or always tell the truth.
   Encode statements like "A says: B is a liar" as booleans and `check-sat`.

5. **SEND + MORE = MONEY** (cryptarithmetic): 8 distinct digits, leading digits
   nonzero, the addition holds. A great `Distinct` + arithmetic exercise.

Reference: Z3 guide https://microsoft.github.io/z3guide/ · SMT-LIB https://smt-lib.org
