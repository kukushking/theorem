# Results log — Rung 4

Fill this in as you run. **One section per run.** The point isn't a clean win —
it's to track *what each prover actually does on each target* so you build a
real feel for where today's LLM-based theorem proving sits.

This file is the **deliverable** for Rung 4. If you want a private working copy
that doesn't get committed, save it as `MY_RESULTS.md` — that filename is
git-ignored.

> **Tip.** Don't over-curate. A messy run with a weird failure is more useful
> than a clean "it worked" — surprises and dead ends are where the learning is.

---

## Run N — `<YYYY-MM-DD>` · `<hardware: e.g. M3 Air 16 GB>` · `<prover + model>`

Command you ran:

```bash
# e.g. uv run python agent.py --all --prover local
```

### Per-target outcomes

| Target | Result | Attempts | Final proof | Notes |
|---|:---:|---:|---|---|
| `add_self_eq_two_mul` (`n + n = 2 * n`) | ? | ? / 5 | | |
| `and_comm_easy` (`p ∧ q → q ∧ p`) | ? | ? / 5 | | |
| `binomial_square` (`(a+b)^2 = a^2 + 2ab + b^2`) | ? | ? / 5 | | |

**Score: ? / 3.** Total wall-clock: `<time>`.

### What surprised you?

> *Did a target succeed unexpectedly? Did the model produce something weird?
> Did the retry loop converge or just spiral? Did the same model behave
> differently across targets?*

### What didn't work and why?

> *Lean errors, prompt issues, model brain-rot, network failures, API quotas,
> account state, broken GGUFs, mis-matched API versions, …  Note any setup
> footguns the README didn't warn you about so you can update it.*

### Throughput

| Stage | Time |
|---|---|
| Mathlib load (first call) | |
| Per-attempt generation | |
| Per-attempt Lean verify | |
| **End-to-end (all targets)** | |

### Observations / lessons

> *Anything that generalises — about this prover, about prompting, about
> local-vs-cloud trade-offs, about which targets break which provers. The kind
> of thing future-you would want to see before starting Run N+1.*

---

## Reflection (after a few runs across different provers)

Once you've done 2–3 runs across different brains (Claude via the Anthropic API
vs a local model; or different local models), write a paragraph or two:

- Where does today's SOTA shine, and where does it crack?
- Did the agent loop *help* (i.e. did attempt-N+1 succeed where attempt-N failed
  with error context), or did the model just produce the same broken proof
  with cosmetic variation?
- What would you change about the prompt, the model choice, or the targets if
  you ran this for real (e.g. against `miniF2F`)?
- Where does the kernel (Lean) save you from yourself?

This reflection is the *real* output of the rung. The proofs are the artefact;
the calibration is the deliverable.
