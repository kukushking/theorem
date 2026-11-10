(*
  Rung 5, part 1 — Coq as a programming language. No logic, no symbols.

  Forget "proof assistant" for ten minutes. Coq is a small functional
  programming language (think OCaml's little sibling). You define functions,
  you run them, you test them. That's this entire file.

  The only new idea, introduced at the very end: a unit test that takes
  `forall` instead of one hard-coded input. That's all a theorem is.

  HOW TO READ THIS RUNG (this matters more than any definition):
  a proof script is NOT meant to be read as text. It's a transcript of an
  interactive session — like a chess scoresheet, the information isn't in
  the moves but in the board after each move. Open this file in VS Code
  with the VsCoq extension, put your cursor after any line, and the goal
  panel shows you the board. Step; watch it change; repeat. Reading .v
  files cold is how this stuff stops making sense.

  Run:  rocq compile program.v
*)

(* ---------- 1. Hello world: a function ---------- *)
(* `nat` = the natural numbers 0, 1, 2, ...  This is just a function. *)

Definition add (a b : nat) : nat := a + b.

(* Run it. `Compute` evaluates right in the compiler — Coq's REPL moment.
   The answer prints when you compile (or hover in VS Code). *)

Compute add 2 3.        (* = 5 : nat *)

(* A recursive function: 1 + 2 + ... + n. `Fixpoint` = recursive `def`.
   Pattern matching, just like OCaml/Rust: a nat is either 0 or S k
   ("successor of k", i.e. k + 1). *)

Fixpoint sum_to (n : nat) : nat :=
  match n with
  | 0 => 0
  | S k => n + sum_to k
  end.

Compute sum_to 10.      (* = 55 : nat *)

(* ---------- 2. Unit tests ---------- *)
(* `Example` is a unit test. `reflexivity` means "run both sides and check
   they come out equal" — it's assertEqual. If the test fails, the file
   does not compile. A test suite the compiler refuses to skip. *)

Example test_add : add 2 3 = 5.
Proof. reflexivity. Qed.

Example test_sum : sum_to 10 = 55.
Proof. reflexivity. Qed.

Example test_sum_edge : sum_to 0 = 0.
Proof. reflexivity. Qed.

(* ---------- 3. The one new idea: a unit test over ALL inputs ---------- *)
(* test_add checks ONE input. What an engineer actually wants to assert is
   "add is commutative for EVERY input" — property-based testing (QuickCheck,
   Hypothesis), except those sample a few hundred cases. A theorem is the
   same property with infinite coverage: `forall` replaces the sampler.

   `lia` is the arithmetic solver you already met in rung 1 (it IS the same
   algorithm family as Z3's integer engine). `intros` just names the inputs,
   like the arguments line of a test function. *)

From Stdlib Require Import Lia.

Theorem add_commutes : forall a b : nat, add a b = add b a.
Proof. intros a b. unfold add. lia. Qed.

(* And the classic: Gauss's closed form for sum_to. You cannot unit-test
   all n; `induction` is how you cover infinity — prove it for 0, prove
   each case follows from the previous one. It's a loop invariant.
   (`nia` = `lia`'s big brother that tolerates multiplication.) *)

Theorem sum_to_gauss : forall n : nat, 2 * sum_to n = n * (n + 1).
Proof.
  intros n.
  induction n as [| k IH].   (* two cases: n = 0, n = S k *)
  - reflexivity.             (* base: just run it *)
  - simpl. nia.              (* step: arithmetic, given IH *)
Qed.

(* That's the entire conceptual content of formal verification:
     program  +  property over all inputs  +  a checker that accepts
   no hand-waving. Everything else in this rung is vocabulary. *)

(*
  EXERCISES — replace `Admitted.` with a proof ending in `Qed.`
  (Admitted = "trust me", and the kernel literally books it as an axiom.)
*)

(* 1. Write the unit test's proof. One tactic. *)
Example test_add_big : add 1000 2000 = 3000.
Proof. Admitted.

(* 2. `double` is below. Prove it agrees with add-to-itself, for all n.
      Two or three tactics — mimic add_commutes. *)
Definition double (n : nat) : nat := 2 * n.

Theorem double_is_add : forall n : nat, double n = add n n.
Proof. Admitted.

(* 3. The engineer's theorem: refactoring is safe. `sum_fast` is the
      tail-recursive version of sum_to (constant stack — the version you'd
      actually ship). Prove the refactor changed nothing. The helper lemma
      is given; its trick is that the induction hypothesis must quantify
      over `acc` (that's the `revert acc` dance). Prove the lemma by
      induction, then the theorem falls out of it. *)
Fixpoint sum_acc (n acc : nat) : nat :=
  match n with
  | 0 => acc
  | S k => sum_acc k (n + acc)
  end.

Definition sum_fast (n : nat) : nat := sum_acc n 0.

Lemma sum_acc_spec : forall n acc, sum_acc n acc = sum_to n + acc.
Proof. Admitted.

Theorem refactor_safe : forall n, sum_fast n = sum_to n.
Proof. Admitted.
