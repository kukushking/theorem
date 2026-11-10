(*
  Rung 5, part 2 — verify a PROGRAM, not a theorem.

  Everything so far in this repo proved mathematical statements. This file does
  what CompCert, Iris, and Fiat-Crypto do at industrial scale: write a program,
  write a SPECIFICATION of what it should do, and prove — kernel-checked — that
  the program meets the spec.

  The program: insertion sort.
  The spec:    (1) the output is sorted, AND
               (2) the output is a permutation of the input.

  Why BOTH halves? Because each half alone is gameable:
    - `fun l => []` returns a sorted list every time.      (passes 1, fails 2)
    - `fun l => l`  returns a permutation every time.      (passes 2, fails 1)
  Only the conjunction forces the program to actually sort. Writing specs that
  can't be gamed is THE hard problem of software verification — provers check
  the proof, but nothing checks that the spec says what you meant.

  Run:  rocq compile verified.v
*)

From Stdlib Require Import List Arith Lia Permutation.
Import ListNotations.

(* ---------- 1. The program ---------- *)
(* Ordinary functional code. Nothing proof-flavored about it: this is the same
   insertion sort you'd write in OCaml or Haskell. *)

Fixpoint insert (x : nat) (l : list nat) : list nat :=
  match l with
  | [] => [x]
  | h :: t => if x <=? h then x :: h :: t else h :: insert x t
  end.

Fixpoint sort (l : list nat) : list nat :=
  match l with
  | [] => []
  | h :: t => insert h (sort t)
  end.

(* Programs compute — the kernel can run them. *)
Example sort_demo : sort [3; 1; 4; 1; 5] = [1; 1; 3; 4; 5].
Proof. reflexivity. Qed.

(* ---------- 2. The specification ---------- *)
(* "Sorted" as an inductive predicate: a list is sorted if it's empty, a
   singleton, or its first two elements are in order and the tail is sorted.
   The spec is DATA the kernel checks against — not a comment, not a test. *)

Inductive sorted : list nat -> Prop :=
| sorted_nil  : sorted []
| sorted_one  : forall x, sorted [x]
| sorted_cons : forall x y l, x <= y -> sorted (y :: l) -> sorted (x :: y :: l).

(* The other half — "same elements" — is the standard library's `Permutation`.
   Reusing a library's spec vocabulary is half the craft; rung 3's Mathlib
   lesson, software edition. *)

(* ---------- 3. The proof ---------- *)
(* One helper lemma per half, then induction stitches them together. This
   extrinsic style — program first, proof second, connected by theorems —
   is how most industrial verification works. (The intrinsic alternative:
   give `sort` a TYPE that only sorted permutations inhabit, so the program
   can't compile unless it's correct. Elegant, harder to engineer.) *)

Lemma insert_sorted : forall x l, sorted l -> sorted (insert x l).
Proof.
  intros x l H.
  induction H; simpl.
  - apply sorted_one.
  - destruct (x <=? x0) eqn:E.
    + apply Nat.leb_le in E. apply sorted_cons. exact E. apply sorted_one.
    + apply Nat.leb_gt in E. apply sorted_cons. lia. apply sorted_one.
  - destruct (x <=? x0) eqn:E1.
    + apply Nat.leb_le in E1.
      apply sorted_cons. exact E1. apply sorted_cons; assumption.
    + apply Nat.leb_gt in E1.
      simpl in IHsorted. destruct (x <=? y) eqn:E2.
      * apply sorted_cons. lia. exact IHsorted.
      * apply sorted_cons. exact H. exact IHsorted.
Qed.

Theorem sort_sorted : forall l, sorted (sort l).
Proof.
  induction l as [| h t IH]; simpl.
  - apply sorted_nil.
  - apply insert_sorted. exact IH.
Qed.

Lemma insert_perm : forall x l, Permutation (x :: l) (insert x l).
Proof.
  intros x l.
  induction l as [| h t IH]; simpl.
  - apply Permutation_refl.
  - destruct (x <=? h).
    + apply Permutation_refl.
    + apply Permutation_trans with (h :: x :: t).
      * apply perm_swap.
      * apply perm_skip. exact IH.
Qed.

Theorem sort_perm : forall l, Permutation l (sort l).
Proof.
  induction l as [| h t IH]; simpl.
  - apply Permutation_refl.
  - apply Permutation_trans with (h :: sort t).
    + apply perm_skip. exact IH.
    + apply insert_perm.
Qed.

(* The contract, in one theorem. *)
Theorem sort_correct : forall l, sorted (sort l) /\ Permutation l (sort l).
Proof.
  intros l. split.
  - apply sort_sorted.
  - apply sort_perm.
Qed.

(* ---------- 4. The audit ---------- *)
(* Same ritual as every proof this repo ships. *)

Print Assumptions sort_correct.
(* => Closed under the global context *)

(*
  EXERCISES — replace `Admitted.` with a proof ending in `Qed.`, recompile,
  and re-run `Print Assumptions` on your theorem. Hints at the bottom of
  the README.
*)

(* 1. Programs compute: the kernel can check a concrete run outright.
      One tactic. *)
Theorem ex_sort_example : sort [2; 0; 2; 6] = [0; 2; 2; 6].
Proof. Admitted.

(* 2. A resource property: inserting adds exactly one element.
      Induction on l; in the cons case, case on the comparison
      (`destruct (x <=? h)`) before simplifying. *)
Theorem ex_insert_length : forall x l, length (insert x l) = S (length l).
Proof. Admitted.

(* 3. The spec-gaming demo, live. Here is the "sort" that games half the spec: *)
Definition cheat_sort (l : list nat) : list nat := [].

(* Prove the cheat satisfies the SORTEDNESS half — one constructor. Then try
   (on paper or in anger) to prove `Permutation l (cheat_sort l)` and watch
   the goal collapse to the unprovable `Permutation [1] []`. The permutation
   half is the only thing standing between this program and a merged PR. *)
Theorem ex_cheat_is_sorted : forall l, sorted (cheat_sort l).
Proof. Admitted.
