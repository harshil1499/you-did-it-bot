"""Coaching loop: the heart of the product.

Evaluates one reported item (a weekly priority or a task) against the writing
standard (writing_standard.md) and returns a structured verdict. The model client
is injectable so the verdict logic unit-tests without an API key or network.

The multi-turn loop (ask -> revise -> re-evaluate) is driven by the conversation
handler (T2); this module owns a single evaluation and the accept / push-back /
escape-hatch decision.
"""

from __future__ import annotations

import json
import os
import re

import config

# Cap the back-and-forth so a stubborn item can't loop forever. On hitting the cap
# we store it flagged as un-coached, so we can see where the standard fails people.
MAX_ROUNDS = 3

_STANDARD_PATH = os.path.join(os.path.dirname(__file__), "writing_standard.md")

_SYSTEM_TEMPLATE = """You are a weekly check-in coach. Evaluate ONE reported item \
(a priority or a task) against the writing standard below.

Return ONLY a JSON object, no prose around it:
{{"clean": true|false, "feedback": "string", "suggested_rewrite": "string"}}

Rules:
- clean=true only if the item clears all five SMART elements. Then leave feedback empty.
- If clean=false, name the specific gap(s) in plain language and give a concrete
  suggested_rewrite the person can accept or adapt.
- For "Relevant", require the person to state how the item moves its metric; do NOT
  judge whether it will actually work. That is their call, not yours.
- Be specific and brief.

WRITING STANDARD:
{standard}
"""


def _load_standard() -> str:
    with open(_STANDARD_PATH, encoding="utf-8") as f:
        return f.read()


def build_system_prompt() -> str:
    return _SYSTEM_TEMPLATE.format(standard=_load_standard())


def parse_verdict(text: str) -> dict:
    """Parse the model's JSON verdict robustly (tolerates code fences / stray text)."""
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object in model output: {text!r}")
        data = json.loads(match.group(0))
    return {
        "clean": bool(data.get("clean", False)),
        "feedback": str(data.get("feedback", "")).strip(),
        "suggested_rewrite": str(data.get("suggested_rewrite", "")).strip(),
    }


def evaluate_item(item_text: str, client=None, model: str | None = None) -> dict:
    """Evaluate one item; return {"clean", "feedback", "suggested_rewrite"}.

    client: an Anthropic-style client with messages.create(...). Injected in tests;
    created from config.ANTHROPIC_API_KEY when omitted.
    """
    if client is None:
        import anthropic

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    model = model or config.ANTHROPIC_MODEL

    response = client.messages.create(
        model=model,
        max_tokens=400,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": item_text}],
    )
    return parse_verdict(response.content[0].text)


def decide(rounds: int, verdict: dict) -> str:
    """Map (rounds so far, verdict) to an action.

    'accept'            -> clean, store it.
    'accept_with_flag'  -> not clean but cap reached; store, mark un-coached.
    'push_back'         -> not clean, ask for a revision.
    """
    if verdict.get("clean"):
        return "accept"
    if rounds >= MAX_ROUNDS:
        return "accept_with_flag"
    return "push_back"
