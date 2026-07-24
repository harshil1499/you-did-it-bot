"""Local demo / manual test for the coaching loop. Runs the REAL model.

Usage:
    python demo_coaching.py                 # run the sample suite
    python demo_coaching.py "your task"     # evaluate one item

Needs ANTHROPIC_API_KEY. It reads a local .env (gitignored) if present, so you
never paste a key into a chat or commit it.

This is the Friday safety net: it proves the coaching works on real input even
before the Slack app (H8/H9) is live.
"""

from __future__ import annotations

import os
import sys


def _load_dotenv():
    path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


_load_dotenv()

import coaching  # noqa: E402

# A few items spanning clearly-bad to clearly-good, including leadership's anchors.
SAMPLES = [
    "A conversation from a campaign through the summer.",      # leadership's fail anchor
    "Grow Discord.",                                            # vague, no number/date
    "Confirm renewal for 15 whitelisters in June and 25 for July.",  # leadership's pass anchor
    "Work on retention this quarter.",                          # no deliverable/metric/date
]


def run_loop(item: str, max_rounds: int = coaching.MAX_ROUNDS) -> None:
    """Simulate the full loop: evaluate, and if not clean, adopt the suggested
    rewrite and re-evaluate, up to the cap. Shows what a person would experience."""
    print(f"\n=== ITEM: {item}")
    current = item
    for rnd in range(1, max_rounds + 1):
        verdict = coaching.evaluate_item(current)
        action = coaching.decide(rnd, verdict)
        if verdict["clean"]:
            print(f"  round {rnd}: CLEAN -> {action}")
            return
        print(f"  round {rnd}: not clean -> {action}")
        print(f"    feedback: {verdict['feedback']}")
        print(f"    suggested: {verdict['suggested_rewrite']}")
        if action == "accept_with_flag":
            print("    (cap reached; stored flagged as un-coached)")
            return
        # Person adopts the suggestion; re-evaluate it next round.
        current = verdict["suggested_rewrite"] or current


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY not found. Put it in a local .env "
            "(ANTHROPIC_API_KEY=sk-ant-...); .env is gitignored."
        )
    items = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else SAMPLES
    for item in items:
        run_loop(item)


if __name__ == "__main__":
    main()
