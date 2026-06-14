"""The agent loop.

For each target:
  1. ask the prover for a proof, given the goal + any prior errors
  2. assemble the full Lean snippet (imports + theorem + body)
  3. run it through the verifier
  4. if ok → done; if not → feed the errors back to the prover and try again
  5. give up after MAX_ATTEMPTS

Usage:
    uv run python agent.py --target add_self_eq_two_mul --prover claude
    uv run python agent.py --all --prover local
"""
from __future__ import annotations

import argparse
from pathlib import Path

from prover import Prover
from targets import TARGETS, Target, get_target
from verifier import Verifier

# 03-lean-math sits one level above this folder.
PROJECT_DIR = Path(__file__).resolve().parent.parent / "03-lean-math"
MAX_ATTEMPTS = 5


def build_lean_code(target: Target, proposal: str) -> str:
    """Assemble the final Lean snippet to submit.

    Some provers return just the body (`by omega`); others return the whole
    theorem with proof. We accept both and normalise into one valid snippet.
    """
    body = proposal.strip()
    # Whole theorem returned? Use it as-is (just prepend imports).
    if body.startswith("theorem ") or body.startswith("example ") or body.startswith("lemma "):
        return f"{target.imports}\n\n{body}\n"
    # Otherwise it's a body. Make sure it starts with `:= by` or `:=`.
    if body.startswith(":="):
        glue = ""
    elif body.startswith("by "):
        glue = ":= "
    else:
        glue = ":= by "
    return f"{target.imports}\n\n{target.statement} {glue}{body}\n"


def attempt(prover: Prover, target: Target, verifier: Verifier) -> bool:
    prior_errors: list[str] = []
    for n in range(1, MAX_ATTEMPTS + 1):
        print(f"\n[{prover.name}] {target.name} — attempt {n}/{MAX_ATTEMPTS}")
        proposal = prover.propose(target.statement, prior_errors)
        preview = proposal.replace("\n", " ")[:140]
        print(f"  proposed: {preview}{'…' if len(proposal) > 140 else ''}")

        lean_code = build_lean_code(target, proposal)
        result = verifier.verify(lean_code)

        if result.ok:
            print(f"  ✓ PROVED on attempt {n}")
            return True

        for err in result.errors:
            print(f"  ✗ error: {err.splitlines()[0][:140]}")
        if result.has_sorry:
            print(f"  ✗ proof still contains `sorry`")

        prior_errors.append(
            "\n".join(result.errors)
            + (" [proof still contained `sorry`]" if result.has_sorry else "")
        )

    print(f"  ✗ {prover.name} gave up after {MAX_ATTEMPTS} attempts")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-driven Lean prover (Rung 4).")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--target", help="name of one target to attempt")
    g.add_argument("--all", action="store_true", help="attempt all targets")
    parser.add_argument(
        "--prover",
        choices=["claude", "local"],
        required=True,
        help="which LLM backend to use",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="override the prover's default model ID",
    )
    args = parser.parse_args()

    # Lazy import so the unused prover's deps (Anthropic SDK / Ollama) aren't required.
    if args.prover == "claude":
        from provers.claude import ClaudeProver
        prover: Prover = ClaudeProver(model=args.model)
    else:
        from provers.local import LocalProver
        prover = LocalProver(model=args.model)

    print(f"loading Lean project at {PROJECT_DIR} (first call takes ~20s for Mathlib)...")
    verifier = Verifier(PROJECT_DIR)

    targets = TARGETS if args.all else [get_target(args.target)]
    results: list[tuple[str, bool]] = []
    for t in targets:
        ok = attempt(prover, t, verifier)
        results.append((t.name, ok))

    print("\n=== summary ===")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")
    passed = sum(1 for _, ok in results if ok)
    print(f"  {passed}/{len(results)} proved")


if __name__ == "__main__":
    main()
