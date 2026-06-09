"""Coaching loop: the heart of the product.

Evaluates one reported item (a task or a weekly priority) against the writing
standard and returns a structured verdict. Implemented in the coaching bit (T3).
"""

# Filled in T3.
def evaluate_item(item_text: str) -> dict:
    """Return {"clean": bool, "feedback": str, "suggested_rewrite": str}.

    Calls Claude with the writing standard (writing_standard.md) embedded in the
    system prompt plus a few before/after examples, and parses the JSON verdict.
    """
    raise NotImplementedError("Coaching loop lands in T3.")
