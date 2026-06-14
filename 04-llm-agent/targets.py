"""Easy hand-rolled targets for the first smoke tests.

These are deliberately tame — the goal of Rung 4's first run is to prove the
pipeline (brain → Lean → result), not stress-test the model. Each should be a
one-or-two-tactic close for any reasonable brain.

Later we'll add miniF2F / PutnamBench targets in a separate file.
"""
from dataclasses import dataclass


@dataclass
class Target:
    name: str
    imports: str       # e.g. "import Mathlib"
    statement: str     # e.g. "theorem add_self_eq_two_mul (n : Nat) : n + n = 2 * n"
    hint: str = ""     # human-only hint for the README; NOT given to the brain


TARGETS: list[Target] = [
    Target(
        name="add_self_eq_two_mul",
        imports="import Mathlib",
        statement="theorem add_self_eq_two_mul (n : Nat) : n + n = 2 * n",
        hint="linear arithmetic over Nat — `omega` closes this in one step",
    ),
    Target(
        name="and_comm_easy",
        imports="import Mathlib",
        statement="theorem and_comm_easy (p q : Prop) : p ∧ q → q ∧ p",
        hint="intro the hypothesis, then construct the swapped pair",
    ),
    Target(
        name="binomial_square",
        imports="import Mathlib",
        statement="theorem binomial_square (a b : ℝ) : (a + b) ^ 2 = a^2 + 2*a*b + b^2",
        hint="commutative-ring identity — `ring` closes this",
    ),
]


def get_target(name: str) -> Target:
    for t in TARGETS:
        if t.name == name:
            return t
    raise KeyError(f"unknown target: {name!r}. Try one of: {[t.name for t in TARGETS]}")
