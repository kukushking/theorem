/-
  Lean 4 fundamentals — every proof here compiles with CORE Lean only (no Mathlib),
  so `lake build` is instant.

  Best experienced in VS Code with the "Lean 4" extension: put your cursor inside a
  proof and watch the goal state in the infoview update tactic by tactic. From the
  terminal you can also just run:  lake build  (errors mean a broken proof).

  Key idea (Curry–Howard): a proof IS a program, a proposition IS a type. `theorem`
  and `def` are the same thing under the hood.
-/
namespace LeanBasics

/-! ## 1. Propositional logic -/

-- Assume a proof `hp` of `p`, hand it back. (Identity function = identity proof.)
theorem id_imp (p : Prop) (hp : p) : p := hp

-- Modus ponens, tactic style.
theorem mp (p q : Prop) (hpq : p → q) (hp : p) : q := by
  exact hpq hp

-- "And" is commutative. `h.1`/`h.2` project out the two halves; `⟨_, _⟩` builds one.
theorem and_comm' (p q : Prop) : p ∧ q → q ∧ p := by
  intro h
  exact ⟨h.2, h.1⟩

-- "Or" is commutative — needs a case split on which side holds.
theorem or_comm' (p q : Prop) : p ∨ q → q ∨ p := by
  intro h
  cases h with
  | inl hp => exact Or.inr hp
  | inr hq => exact Or.inl hq

/-! ## 2. Computation and `rfl` (things true *by definition*) -/

theorem two_plus_two : 2 + 2 = 4 := rfl
theorem add_zero (n : Nat) : n + 0 = n := rfl   -- holds because `+` recurses on its 2nd arg

/-! ## 3. Induction -/

-- `0 + n = n` is NOT definitional (the recursion is on the right argument), so we induct.
theorem zero_add (n : Nat) : 0 + n = n := by
  induction n with
  | zero => rfl
  | succ k ih => rw [Nat.add_succ, ih]

/-! ## 4. `omega`: a built-in decision procedure for linear arithmetic -/

theorem succ_gt (n : Nat) : n + 1 > n := by omega
theorem cancel (a b : Nat) (h : a + 3 = b + 3) : a = b := by omega

/-
  EXERCISES — replace `sorry` with a real proof. `sorry` compiles but Lean warns,
  which is exactly the signal an LLM prover uses: "is there still a sorry / error?"
-/
theorem ex_and_idem (p : Prop) : p ∧ p → p := by sorry
theorem ex_imp_trans (p q r : Prop) (hpq : p → q) (hqr : q → r) : p → r := by sorry
theorem ex_arith (n : Nat) : n + n = 2 * n := by sorry

end LeanBasics
