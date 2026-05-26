import Mathlib

-- If this file compiles, Mathlib is installed and usable.
-- `ring` is a Mathlib tactic that proves equalities in commutative (semi)rings.
example (a b : ℝ) : (a + b) ^ 2 = a ^ 2 + 2 * a * b + b ^ 2 := by ring

-- `linarith` discharges linear arithmetic goals over ordered fields.
example (x : ℝ) (h : x > 2) : x + 1 > 3 := by linarith

-- A real Mathlib lemma in action: irrationality of √2 is already proven in Mathlib.
example : Irrational (Real.sqrt 2) := irrational_sqrt_two
