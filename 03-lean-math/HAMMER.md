# Hammers — one-button automation in an interactive prover

A **hammer** lets you stand in a proof assistant, point at a goal, and offload it to the
fast automatic engines (SMT/first-order ATPs). Three stages:

1. **Premise selection** — pick a few hundred relevant lemmas from a library of
   hundreds of thousands (an information-retrieval problem; classical = MePo/MaSh,
   neural = Magnushammer-style retrieval).
2. **Translation** — encode the higher-order / dependently-typed goal + premises into
   first-order logic (TPTP) or SMT-LIB.
3. **Reconstruction** — run E / Vampire / Z3 / cvc5; if one succeeds, *replay* a proof
   the prover's trusted kernel accepts (don't trust the external solver blindly).

This is the single highest-leverage automation technique in interactive proving.

---

## Option A — built-in mini-hammers (already in this project)

No install needed. In `LeanMath/Hammer.lean`:
- `exact?` / `apply?` — search all of Mathlib for a lemma that closes/advances the goal.
  This *is* premise selection, done interactively. (Run inside VS Code to see suggestions.)
- `aesop` — Mathlib's general-purpose proof-search tactic.
- `omega` (linear int/nat), `linarith`/`nlinarith` (linear/nonlinear real arithmetic),
  `ring` (commutative-ring equalities), `polyrith` (calls external CAS).

## Option B — LeanHammer (the real Lean hammer)

`by hammer` = neural/MePo premise selection + `lean-auto` translation + Zipperposition +
`Duper` reconstruction. Repo: https://github.com/JOSHCLUNE/LeanHammer

Add to `lakefile.toml` (pin a tag compatible with your Mathlib/Lean version —
check the repo's README for the tag matching `v4.30.0-rc2`):
```toml
[[require]]
name = "Hammer"
git  = "https://github.com/JOSHCLUNE/LeanHammer"
rev  = "<compatible-tag>"
```
Then `cd 03-lean-math && lake update Hammer && lake build`, and use `by hammer` on a goal.
(Heads-up: LeanHammer tracks recent Mathlib closely; if the tags don't line up with
v4.30.0-rc2, either bump the project or use Option A / Option C meanwhile.)

## Option C — Isabelle Sledgehammer (the original, cleanest out-of-the-box)

If you want to *feel* a hammer with zero version-wrangling, install Isabelle and type
`sledgehammer` on a goal — it ships with E/Vampire/Z3/cvc5 bundled and reconstructs via
`metis`/`smt`. Download: https://isabelle.in.tum.de (macOS Apple-Silicon app).
Docs: https://isabelle.in.tum.de/dist/doc/sledgehammer.pdf

Different language/ecosystem than Lean, but the best single demo of the full
select → translate → solve → reconstruct loop.
