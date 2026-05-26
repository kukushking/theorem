import Mathlib
/-
  Built-in "mini-hammers" in Mathlib — automation you get for free. Every proof here
  is closed entirely by a single search/decision tactic. Check from the terminal:
    cd 03-lean-math && lake env lean LeanMath/Hammer.lean   (no output = all proved)
-/

-- aesop: general-purpose proof search (logic, basic structure).
example (p q : Prop) (h : p ∧ q) : q ∧ p := by aesop

-- omega: complete decision procedure for linear integer/natural arithmetic.
example (n : ℕ) (h : n + 2 = 5) : n = 3 := by omega

-- linarith: linear arithmetic over ordered fields.
example (x y : ℝ) (h1 : x ≤ y) (h2 : y ≤ x) : x = y := by linarith

-- ring: equalities in any commutative ring.
example (a b : ℝ) : (a - b) * (a + b) = a ^ 2 - b ^ 2 := by ring

-- nlinarith: nonlinear arithmetic, here given the hint that squares are nonnegative.
example (x : ℝ) : x ^ 2 ≥ 0 := by nlinarith [sq_nonneg x]

/-
  INTERACTIVE library search (run these in VS Code and click the "Try this" suggestion —
  this is premise selection by hand):
      example : 2 + 2 = 4 := by exact?
      example (a b : ℝ) : a + b = b + a := by apply?

  For a *real* hammer (`by hammer`: premise selection -> FOL/SMT -> external solver ->
  reconstruction), see ../HAMMER.md.
-/
