# Automated Theorem Proving + LLMs — Field Research

*Compiled 2026-05-25. Practical, build-first orientation. Numbers move fast; treat
benchmark figures as "as of late 2025 / early 2026" and re-check leaderboards.*

---

## 0. The mental model (read this first)

The field stacks into three layers, plus a newer LLM layer that reuses the others:

1. **Automatic engines** — SAT (propositional), SMT (SAT + theories), first-order ATPs
   (full FOL with equality). Fully automatic, fast, but speak low-level logic.
2. **Interactive Theorem Provers (ITPs / proof assistants)** — Lean, Isabelle, Coq/Rocq,
   HOL. Expressive (dependent/higher-order types), human-guided, trustworthy via a small
   kernel, but tedious.
3. **The "hammer" bridge** — connects layer 2 to layer 1: pick relevant lemmas
   (*premise selection*), *translate* the goal to FOL/SMT, run the engines, then
   *reconstruct* a kernel-checked proof.
4. **LLM provers (the new layer)** — generate proofs/tactics for an ITP (almost always
   **Lean 4**), verified by the kernel. They frequently *call* the classical engines as
   backends. The kernel makes hallucination safe: generation can be wrong, verification
   is sound and cheap.

**Two LLM paradigms** you'll keep meeting:
- **Whole-proof generation**: model emits an entire proof; you compile once; resample on
  failure. Scales with sampling (pass@k) + self-correction from compiler errors.
  (DeepSeek-Prover, Goedel-Prover, Kimina, Seed-Prover.)
- **Stepwise / tactic-level + tree search**: model proposes one tactic per step; a search
  algorithm (best-first, MCTS, HyperTree) explores the proof tree. (ReProver, AlphaProof.)

**Why Lean 4 is the default LLM target:** it's a programming language *and* a prover
(hackable tooling), has **Mathlib** (~274K theorems, the largest formal math library),
a clean tactic model, and nearly every SOTA prover ships Lean 4 checkpoints.

---

## 1. State of the art — LLM provers (2024 → 2026)

### Milestones
- **AlphaProof + AlphaGeometry2 (DeepMind, IMO 2024)** — first AI at **silver-medal**
  standard: 28/42. AlphaProof = Gemini-based LM + AlphaZero-style RL search in **Lean**
  (solved 3/6, incl. the hardest P6); AlphaGeometry2 = neuro-symbolic (LM guides the DDAR
  symbolic engine), solves ~83% of last-25-years IMO geometry, solved IMO-2024 P4 in 19s.
- **IMO 2025 — three different AI golds (35/42), three different routes:**
  | System | Org | Verified? | Formal or NL? |
  |---|---|---|---|
  | **Gemini Deep Think** | DeepMind | Yes — officially graded/certified by IMO | **Natural language** prose, within the 4.5h limit |
  | **Experimental reasoning model** | OpenAI | Graded by 3 ex-IMO medalists, not IMO-certified | **Natural language**, no tools |
  | **Aristotle** | Harmonic | **Machine-checked** | **Fully formal Lean 4**, 5/6 (arXiv 2510.01346) |
  The Gemini/OpenAI golds are *not machine-verifiable* — which is exactly why the formal
  track (Aristotle, Seed-Prover) matters. The unsolved 6th problem (combinatorics) stumped
  all three. **Combinatorics remains the universal weak spot.**

### Open / published prover models (most are downloadable)
| System | Org | Year | Base / size | Method | Headline numbers |
|---|---|---|---|---|---|
| DeepSeek-Prover-V1 | DeepSeek | 2024-05 | DeepSeekMath-7B | 8M synthetic statements, expert iteration | miniF2F ~50% |
| DeepSeek-Prover-V1.5 | DeepSeek | 2024-08 | 7B | RL from prover feedback (RLPAF) + RMaxTS (MCTS) | miniF2F 63.5%, ProofNet 25.3% |
| DeepSeek-Prover-V2 | DeepSeek | 2025-04 | **671B** + 7B | Subgoal decomposition (V3 CoT) → RL | miniF2F 88.9%, PutnamBench 49/658 |
| Kimina-Prover | Numina/Moonshot | 2025-04 | Qwen2.5-72B | Large-scale RL, "formal reasoning pattern", whole-proof | miniF2F 80.7% (then-SOTA); 7B/1.5B distills released |
| Goedel-Prover-V1 | Princeton PLI | 2025-02 | 7B | Expert iteration over self-proved library | PutnamBench 7 @ pass@512 (1st at the time) |
| **Goedel-Prover-V2** | Princeton PLI | 2025-08 | **8B & 32B** | Scaffolded data synthesis + self-correction + checkpoint averaging | 32B: miniF2F 90.4%; PutnamBench 86 @ pass@184. **8B matches the 671B DeepSeek model (~100× smaller).** Fully open. |
| Seed-Prover | ByteDance | 2025-07 | Seed model | Lemma-style whole-proof + test-time refinement | Saturates miniF2F; >50% PutnamBench; IMO-2025 5/6 formal |
| **Seed-Prover 1.5** | ByteDance | 2025-12 | Seed | **Agentic** (interacts w/ Lean via lemmas) + agentic RL "learns from experience" | Self-reports PutnamBench **88% (580/660)**; pushed onto graduate/PhD sets (FATE-H 80%, FATE-X 33%) |
| Lean-STaR | CMU et al. | 2024 (ICLR'25) | InternLM2-7B | NL "thoughts" before each tactic + expert iteration | miniF2F 34.8–45.4% @ pass@32 |

### The bleeding edge (early–mid 2026) — agentic provers
The frontier has shifted from "one big model + sampling" to **agents**: an LLM that
plans informally, searches a library, calls Lean, reads errors, and recursively
decomposes goals into lemmas.
- **Hilbert** (Apple + UC San Diego) — "recursively building formal proofs with informal
  reasoning." With Gemini 2.5 Pro: PutnamBench **70% pass rate / 462 solved**, miniF2F up
  to 99.2%. (openreview GN8OdkTo3B)
- **Aleph Prover** (Logical Intelligence) — currently **#1 on the public PutnamBench
  leaderboard, 500/660 solved**, surpassing Hilbert.
- **Ax-Prover** (arXiv 2510.12787) — deep-reasoning agentic framework spanning math **and
  quantum physics** theorems.
- **"A Minimal Agent for Automated Theorem Proving"** (Requena et al., ICML 2026,
  arXiv 2602.24273) — *the most important paper for you*. Shows a **deliberately simple**
  agent (iterative refinement + library search + context management) is competitive with
  elaborate systems at far lower cost, and **iterative refinement beats single-shot**.
  Open-source — an ideal reference implementation to build on.

> **Caveat on numbers:** self-reported figures (e.g. Seed-Prover 1.5's 580/660) and the
> verified public leaderboard (Aleph 500/660, Hilbert 462) use different denominators
> (Lean subset cited 658–672), different pass@k budgets, and different verification rules.
> Don't compare across rows naively.

---

## 2. Benchmarks

| Benchmark | Scope / size | Status |
|---|---|---|
| **miniF2F** | 244 test (488 total) HS/Olympiad, formalized for Lean/Isabelle/Coq/Metamath | **Saturated** (~99–100%). Known label errors ("miniF2F revisited", arXiv 2511.03108). |
| **ProofNet** | 186 undergrad analysis/algebra | Largely superseded. |
| **PutnamBench** | 1724 formalizations of Putnam 1962–2025 (Lean subset ~660) | **The current frontier.** Live leaderboard at trishullab.github.io/PutnamBench. |
| **FormalMATH** | 5,560 problems, HS→undergrad (arXiv 2505.02735) | Far from saturated; strong algebra bias, weak elsewhere. |
| **CombiBench** | Combinatorics (Moonshot) | New, hard; the universal weak spot. |
| **FATE-H / FATE-X** | Graduate / PhD-level (Seed-Prover 1.5) | The new ceiling. |
| **TPTP / CASC** | Raw first-order logic problems, annual ATP world championship | Tests *classical engines*, not proof-finding intelligence. |
| **SMT-LIB / SMT-COMP** | Per-theory SMT problems | Tests SMT solver horsepower. |

**Key distinction:** TPTP/SMT-COMP measure the *engines*; miniF2F/PutnamBench measure the
*proof-finding intelligence* (now usually an LLM) sitting on top of them.

---

## 3. Practical tooling — what you actually install

### Lean 4 + Mathlib
```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh        # toolchain manager
lake +leanprover-community/mathlib4:lean-toolchain new myproj math
cd myproj && lake exe cache get && lake build                 # cache get is CRITICAL
```
Use the VS Code "Lean 4" extension for the interactive infoview.

### Programmatic Lean (build your agent loop here)
| Tool | Lang | Install | Notes |
|---|---|---|---|
| `leanprover-community/repl` | Lean | `lake exe repl` | Official low-level JSON REPL; everything builds on it |
| **LeanInteract** | Python | `pip install lean-interact` | Cleanest Python wrapper over the REPL — **best beginner choice** |
| Pantograph / PyPantograph | Lean+Py | `uv add git+...PyPantograph` | Independent subgoals, MCTS-friendly, sketch+fill |
| Kimina Lean Server | — | — | High-throughput verification backend for batch eval |

### In-editor LLM tactic suggestion (gentlest on-ramp)
- **llmstep** — `llmstep "prefix"` tactic → Python server runs an LLM → checks in Lean.
  CPU server works with **zero GPU** (ByT5-300M). Repo: wellecks/llmstep.
- **Lean Copilot** — runs LLMs *inside* Lean via CTranslate2 FFI. `suggest_tactics`,
  `search_proof`, `select_premises`. Repo: lean-dojo/LeanCopilot.

### Data + environment
- **LeanDojo** (`pip install lean-dojo`) — traces a Lean repo to extract
  (proof state, tactic, premises); also a gym to apply tactics and read new states.
  Benchmark 4: 122,517 proofs / 259,580 tactics / 167,779 premises from mathlib4.
- **ReProver** — retrieval-augmented tactic generator (ByT5-small, CPU-runnable).
  HF: `kaiyuy/leandojo-lean4-tacgen-byt5-small`.
- **LeanAgent** (ICLR'25) — lifelong-learning agent over GitHub Lean repos; proved 162
  theorems humans hadn't. Inference runs on 1 GPU; full training is cluster-scale.

### The hammer (classical automation in an ITP)
- **Sledgehammer** (Isabelle) — the original; type `sledgehammer` on a goal. Calls
  E/Vampire/Z3/cvc5, reconstructs via `metis`. Best out-of-the-box automation.
- **LeanHammer** (`by hammer`) — first end-to-end domain-general Lean hammer: neural/MePo
  premise selection + lean-auto translation + Zipperposition + Duper reconstruction.
- **CoqHammer** (`hammer.`) — the Coq/Rocq analog.

### Classical engines (worth touching once)
- **Z3** (`pip install z3-solver`) / **cvc5** — SMT, `.smt2` format. Highest industrial
  leverage (Dafny, F*, Rust verifiers, etc.).
- **E**, **Vampire** — first-order ATPs; or submit TPTP files to **SystemOnTPTP** web
  service without installing anything.

### Datasets for fine-tuning
- LeanDojo Benchmark 4 (tactic-step + premise retrieval)
- Lean Workbook / Lean-Workbook-Plus (~140K NL↔Lean autoformalized statements)
- DeepSeek-ProverBench (325 problems incl. AIME)
- FormalMATH (5,560)

---

## 4. Key techniques to understand

- **Expert iteration / RL from prover feedback** — generate proofs, keep the verified
  ones, retrain, repeat. The core engine behind almost every prover. Lean's pass/fail is
  a free reward signal (DeepSeek's RLPAF, Goedel/Seed RL loops).
- **Premise selection** — an information-retrieval problem over a math library. Classical:
  MePo (symbolic), MaSh (naive Bayes). Neural: DeepMath (2016, first), Magnushammer
  (contrastive transformer retrieval, ICLR'24 — 59.5% vs 38.3% on PISA). Great first ML
  project: encode facts, build an index, measure recall@k against known proof deps.
- **Proof search** — best-first, beam, MCTS, and **HyperTree Proof Search (HTPS)**
  (Lample et al., NeurIPS'22): proofs are AND/OR hypertrees (a tactic spawns multiple
  subgoals that must *all* close), expanded with policy+value nets and online training.
- **Autoformalization** — NL math → formal. Wu et al. 2022 (few-shot, ~25%). **DSP
  "Draft, Sketch, Prove"** (ICLR'23): LLM drafts informal proof → sketches a formal proof
  with holes → **Sledgehammer fills the holes** (miniF2F 20.9%→39.3%). The canonical
  "LLM intuition + classical rigor" pattern. Danger: silent mistranslation that changes
  the math.

---

## 5. Compute reality (single GPU / Apple Silicon)

- **Tiny models (ByT5-small ~300M)** — ReProver/llmstep/Lean Copilot defaults. CPU-fine.
  Zero barrier; ideal for learning the tactic-step loop.
- **7B prover models (the sweet spot)** — DeepSeek-Prover-V2-7B, Goedel-Prover-SFT.
  ~14GB BF16 → fits a 24GB card (3090/4090). **4-bit quant ~4–6GB → runs on a 16GB+
  Apple Silicon Mac** via llama.cpp / Ollama / MLX (40–120 tok/s). 8GB is not enough.
- **LoRA/QLoRA fine-tuning** of a 7B is feasible on one 24GB GPU (or MLX-LoRA on a Mac).
- **Needs a cluster:** training ReProver/LeanAgent from scratch, RL/expert-iteration loops,
  the 671B / 32B frontier models, high pass@k search at scale.

For an agentic project, the cheapest strong path today is to use a **frontier API model**
(Claude / Gemini / GPT) as the reasoning brain and Lean (local, free) as the verifier —
exactly what Hilbert and the "Minimal Agent" do.

---

## 6. Suggested learning/build ladder

0. **Lean tutorial** — Natural Number Game (web, no install) → "Mathematics in Lean".
1. **SMT warm-up** — `pip install z3-solver`, solve a few SMT-LIB puzzles. Fast win, most
   transferable to industry.
2. **Feel the hammer** — install Isabelle, press `sledgehammer`; or LeanHammer `by hammer`.
3. **Tactic-step loop** — LeanInteract + ReProver ByT5: feed a goal, get a tactic, apply,
   read the new state. Wrap a best-first search around it.
4. **Whole-proof loop** — run DeepSeek-Prover-V2-7B (4-bit via Ollama) on miniF2F: model
   emits a whole proof → LeanInteract verifies → log pass/fail (your own mini-leaderboard).
5. **Build an agent** — reproduce the "Minimal Agent" (arXiv 2602.24273): frontier API
   model + Lean verifier + iterative refinement on compiler errors + library search.
   This is the live frontier and is achievable solo.
6. **Pick a research edge** — combinatorics (everyone's weak spot), better premise
   selection, autoformalization quality, or cheaper agentic search.

---

## 7. Sources

**Systems & results**
- AlphaProof/Geometry silver — deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/
- AlphaProof (Nature) — nature.com/articles/s41586-025-09833-y
- AlphaGeometry2 — arxiv.org/abs/2502.03544
- DeepSeek-Prover V1/V1.5/V2 — arxiv.org/abs/2405.14333, /2408.08152, /2504.21801
- Kimina-Prover — arxiv.org/abs/2504.11354 ; github.com/MoonshotAI/Kimina-Prover-Preview
- Goedel-Prover V1/V2 — arxiv.org/abs/2502.07640, /2508.03613 ; blog.goedel-prover.com
- Seed-Prover — arxiv.org/abs/2507.23726 ; Seed-Prover 1.5 — arxiv.org/abs/2512.17260
- Lean-STaR — arxiv.org/abs/2407.10040 ; HTPS — arxiv.org/abs/2205.11491
- Gemini Deep Think IMO gold — deepmind.google/blog/advanced-version-of-gemini-with-deep-think-officially-achieves-gold-medal-standard-at-the-international-mathematical-olympiad/
- OpenAI IMO 2025 — simonwillison.net/2025/Jul/19/openai-gold-medal-math-olympiad/
- Harmonic Aristotle — arxiv.org/abs/2510.01346 ; github.com/harmonic-ai/IMO2025
- Hilbert — openreview.net/pdf?id=GN8OdkTo3B ; Aleph — logicalintelligence.com/aleph-prover.html
- Ax-Prover — arxiv.org/abs/2510.12787
- **Minimal Agent for ATP** — arxiv.org/abs/2602.24273

**Tooling**
- Lean/Mathlib — github.com/leanprover-community/mathlib4 ; lean-lang.org/install
- LeanDojo/ReProver — github.com/lean-dojo/LeanDojo, /ReProver ; leandojo.org
- Lean Copilot — github.com/lean-dojo/LeanCopilot ; llmstep — github.com/wellecks/llmstep
- LeanInteract — github.com/augustepoiroux/LeanInteract ; Pantograph — github.com/stanford-centaur/PyPantograph
- LeanAgent — github.com/lean-dojo/LeanAgent ; arxiv.org/abs/2410.06209
- Sledgehammer — isabelle.in.tum.de/dist/doc/sledgehammer.pdf ; PISA — github.com/albertqjiang/Portal-to-ISAbelle
- LeanHammer — github.com/JOSHCLUNE/LeanHammer ; arxiv.org/abs/2506.07477
- CoqHammer — coqhammer.github.io ; Tactician — github.com/coq-tactician ; Graph2Tac — github.com/IBM/graph2tac
- Z3 — github.com/Z3Prover/z3 ; cvc5 — cvc5.github.io ; Vampire — vprover.github.io ; E — github.com/eprover/eprover
- TPTP — tptp.org ; SystemOnTPTP — tptp.org/cgi-bin/SystemOnTPTP ; SMT-LIB — smt-lib.org

**Benchmarks**
- miniF2F — arxiv.org/abs/2109.00110 ; revisited — arxiv.org/abs/2511.03108
- PutnamBench — github.com/trishullab/PutnamBench ; leaderboard trishullab.github.io/PutnamBench/leaderboard.html
- FormalMATH — arxiv.org/abs/2505.02735 ; CombiBench — moonshotai.github.io/CombiBench/

**Techniques**
- DeepMath premise selection — arxiv.org/abs/1606.04442 ; Magnushammer — arxiv.org/abs/2303.04488
- Autoformalization (Wu) — arxiv.org/abs/2205.12615 ; DSP — arxiv.org/abs/2210.12283
