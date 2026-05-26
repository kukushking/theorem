#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.9"
# dependencies = ["z3-solver"]
# ///
"""
SMT warm-up with Z3 (Python API).

Run with:   uv run 01-smt/examples.py
(uv auto-installs z3-solver from the inline metadata above — no venv needed.)

The big idea that connects SMT to *theorem proving*:
    A formula F is VALID (always true)  <=>  its negation (not F) is UNSAT.
So to "prove" a theorem with an SMT solver, you assert its negation and hope
the solver says `unsat`. This refutation trick is the heart of automated proving.
"""

from z3 import (
    Int, Ints, Bool, Bools, Solver, And, Or, Not, Implies, If,
    Function, IntSort, ForAll, Distinct, sat, unsat, prove,
)


def banner(title):
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


# ---------------------------------------------------------------------------
def example_1_find_a_model():
    """Constraint solving: find integers satisfying some equations."""
    banner("1. Find a model (constraint solving)")
    x, y = Ints("x y")
    s = Solver()
    s.add(x > 0, y > 0, x + 2 * y == 10, x * y == 12)
    print("Constraints: x>0, y>0, x+2y=10, x*y=12")
    if s.check() == sat:
        m = s.model()
        print(f"  SAT  ->  x = {m[x]}, y = {m[y]}")
    else:
        print("  UNSAT (no such integers)")


# ---------------------------------------------------------------------------
def example_2_prove_by_refutation():
    """Prove a theorem by showing its negation is unsatisfiable."""
    banner("2. Prove theorems (validity = unsat of the negation)")

    # 2a. A propositional tautology: (p -> q) and p  implies  q  (modus ponens)
    p, q = Bools("p q")
    claim = Implies(And(Implies(p, q), p), q)
    print("2a. modus ponens:  ((p->q) & p) -> q")
    _check_valid(claim)

    # 2b. An arithmetic fact over the integers: for all x, x+x == 2*x.
    #     z3 reasons about ALL integers here, not just a sample — that's a proof.
    x = Int("x")
    print("2b. arithmetic:  x + x = 2*x  (for every integer x)")
    _check_valid(x + x == 2 * x)

    # 2c. A FALSE claim, to exercise the other branch: x*x == x holds ONLY for
    #     x in {0, 1}, so over all integers it is not valid and z3 returns a
    #     concrete counterexample. (Note: x*x >= x IS valid over the integers —
    #     a good reminder that "obvious" claims need checking against the domain.)
    print("2c. false claim:  x*x = x  (only true for x in {0,1} — expect a counterexample)")
    _check_valid(x * x == x)


def _check_valid(formula):
    """Assert the negation; unsat => the formula is a theorem."""
    s = Solver()
    s.add(Not(formula))
    r = s.check()
    if r == unsat:
        print("    => UNSAT of negation  =>  PROVED (valid)")
    elif r == sat:
        print(f"    => SAT of negation     =>  NOT valid. Counterexample: {s.model()}")
    else:
        print("    => unknown")


# ---------------------------------------------------------------------------
def example_3_graph_coloring():
    """A classic NP problem: can a graph be colored with k colors?
    K4 (complete graph on 4 nodes) needs 4 colors, so 3-coloring is UNSAT."""
    banner("3. Graph 3-coloring (K4 is not 3-colorable)")
    # 4 nodes, each gets a color in {0,1,2}; all pairs are adjacent (complete).
    c = Ints("c0 c1 c2 c3")
    s = Solver()
    for ci in c:
        s.add(And(ci >= 0, ci <= 2))            # 3 colors available
    for i in range(4):
        for j in range(i + 1, 4):
            s.add(c[i] != c[j])                  # adjacent nodes differ
    print("Try 3-coloring K4 (every pair adjacent):")
    print("  ", "SAT (colorable)" if s.check() == sat else "UNSAT -> needs >3 colors")


# ---------------------------------------------------------------------------
def example_4_uninterpreted_functions():
    """SMT does equality reasoning over UNINTERPRETED functions (congruence):
    if x = y then f(x) = f(y), for ANY f. No definition of f required."""
    banner("4. Uninterpreted functions (congruence reasoning)")
    f = Function("f", IntSort(), IntSort())
    x, y = Ints("x y")
    claim = Implies(x == y, f(x) == f(y))
    print("Claim:  x = y  ->  f(x) = f(y)   (f arbitrary)")
    _check_valid(claim)


# ---------------------------------------------------------------------------
def example_5_quantifiers():
    """Quantified reasoning: prove a fact stated with ForAll."""
    banner("5. Quantifiers")
    f = Function("f", IntSort(), IntSort())
    x = Int("x")
    # Hypothesis: f is the doubling function. Then f(3) must be 6.
    s = Solver()
    s.add(ForAll([x], f(x) == 2 * x))   # assume forall x. f(x)=2x
    s.add(f(3) != 6)                    # negation of what we want to prove
    print("Given (forall x. f(x)=2x), prove f(3)=6:")
    print("  ", "PROVED" if s.check() == unsat else "not proved")


if __name__ == "__main__":
    example_1_find_a_model()
    example_2_prove_by_refutation()
    example_3_graph_coloring()
    example_4_uninterpreted_functions()
    example_5_quantifiers()
    print("\nDone. Now open 01-smt/EXERCISES.md and try the puzzles yourself.")
