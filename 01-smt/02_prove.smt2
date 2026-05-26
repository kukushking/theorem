; Run with:  z3 01-smt/02_prove.smt2
;
; Proving a theorem by REFUTATION: a formula is valid iff its negation is unsat.
; Here we "prove" the distributive-ish fact  (a -> b) is equivalent to (not a or b)
; by asserting they DIFFER and checking that's impossible.
(set-logic QF_UF)            ; quantifier-free, uninterpreted functions (here: booleans)

(declare-const a Bool)
(declare-const b Bool)

; Assert the negation of the claim "(a => b)  <=>  (not a or b)".
; If this is UNSAT, the claim is a theorem.
(assert (not (= (=> a b) (or (not a) b))))

(check-sat)      ; -> unsat   means the two sides are always equal => PROVED
