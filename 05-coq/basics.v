(*
  Coq (now "Rocq") fundamentals — the same theorems as rung 2's Basic.lean,
  re-proved in the other major proof assistant. Zero libraries beyond the
  standard prelude; compiles in under a second.

  Run:    rocq compile basics.v     (no output = every proof checked)
  Watch:  VS Code with the "VsCoq" extension gives the live goal view,
          exactly like Lean's infoview.

  Same Curry–Howard story as Lean: a proof is a program, a proposition is a
  type. What changes is the surface: tactics end with a period, `Qed.` seals
  a proof, and `Admitted.` is Coq's `sorry`.
*)

(* ---------- 1. Propositional logic ---------- *)

(* Assume a proof hp of p, hand it back. Same identity-function proof. *)
Theorem id_imp : forall p : Prop, p -> p.
Proof. intros p hp. exact hp. Qed.

(* Modus ponens. *)
Theorem mp : forall p q : Prop, (p -> q) -> p -> q.
Proof. intros p q hpq hp. exact (hpq hp). Qed.

(* "And" is commutative. `destruct` is Lean's `cases`/`obtain`;
   `split` builds the pair that Lean writes ⟨_, _⟩. *)
Theorem and_comm' : forall p q : Prop, p /\ q -> q /\ p.
Proof.
  intros p q h.
  destruct h as [hp hq].
  split.
  - exact hq.
  - exact hp.
Qed.

(* "Or" is commutative — same case split as Lean's `cases ... with inl/inr`. *)
Theorem or_comm' : forall p q : Prop, p \/ q -> q \/ p.
Proof.
  intros p q h.
  destruct h as [hp | hq].
  - right. exact hp.
  - left. exact hq.
Qed.

(* ---------- 2. Computation and reflexivity ---------- *)

(* True by computation, like Lean's `rfl`. *)
Theorem two_plus_two : 2 + 2 = 4.
Proof. reflexivity. Qed.

(* THE FLIP. In Lean, `n + 0 = n` is definitional and `0 + n` needs induction.
   In Coq it is EXACTLY REVERSED: `+` recurses on its FIRST argument here,
   so `0 + n` computes away and `n + 0` is the one that needs work.
   Same theorem, same kernel idea, opposite "trivial" direction — this is
   what "true by definition" actually means: it depends on how `+` was written. *)
Theorem zero_add : forall n : nat, 0 + n = n.
Proof. intros n. reflexivity. Qed.

(* ---------- 3. Induction ---------- *)

Theorem add_zero : forall n : nat, n + 0 = n.
Proof.
  intros n.
  induction n as [| k IH].
  - reflexivity.              (* base: 0 + 0 computes to 0 *)
  - simpl. rewrite IH. reflexivity.
Qed.

(* ---------- 4. `lia`: the built-in linear-arithmetic decision procedure ---------- *)
(* Lean calls it `omega`; Coq's modern name is `lia` (the old Coq tactic
   literally WAS called `omega` — same algorithm lineage, both descend from
   the Omega test. Rung 1's SMT solvers are the industrial version.) *)

From Stdlib Require Import Lia.

Theorem succ_gt : forall n : nat, n + 1 > n.
Proof. intros n. lia. Qed.

Theorem cancel : forall a b : nat, a + 3 = b + 3 -> a = b.
Proof. intros a b h. lia. Qed.

(* ---------- 5. The audit ---------- *)
(* Coq's analog of Lean's `#print axioms`. A closed proof over the prelude
   prints "Closed under the global context" — the kernel vouches for it with
   NO axioms at all. This is the same audit this repo runs on every proof it
   ships (see the merged-contributions section of the root README). *)

Print Assumptions add_zero.

(*
  EXERCISES — replace `Admitted.` with a real proof ending in `Qed.`
  `Admitted.` compiles SILENTLY — but it registers the theorem as an AXIOM.
  Run `Print Assumptions ex_arith.` and the kernel rats it out:
      Axioms: ex_arith : forall n : nat, n + n = 2 * n
  This is exactly Lean's `sorryAx` showing up in `#print axioms` — in both
  assistants, the audit at the kernel is what catches the IOU, which is the
  whole reason this repo runs that audit on every proof it ships.
*)

Theorem ex_and_idem : forall p : Prop, p /\ p -> p.
Proof. Admitted.

Theorem ex_imp_trans : forall p q r : Prop, (p -> q) -> (q -> r) -> p -> r.
Proof. Admitted.

Theorem ex_arith : forall n : nat, n + n = 2 * n.
Proof. Admitted.
