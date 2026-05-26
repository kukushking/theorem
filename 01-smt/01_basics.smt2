; Run with:  z3 01-smt/01_basics.smt2
; This is the SMT-LIB v2 language — the standard input format every SMT solver speaks.
;
; QF_LIA = Quantifier-Free Linear Integer Arithmetic.
(set-logic QF_LIA)

(declare-const x Int)
(declare-const y Int)

(assert (> x 0))
(assert (> y 0))
(assert (= (+ x (* 2 y)) 10))   ; x + 2y = 10   (prefix/Polish notation)

(check-sat)      ; -> sat
(get-model)      ; shows concrete x, y that work
