"""Miss detection and escalation.

Miss deadline: Tuesday 11:00 local (two nudges first, end of day Monday then
Tuesday 11:00). On a miss, post one consolidated message to ESCALATION_CHANNEL_ID
tagging Kayvon. There is no rollup channel; Kayvon reviews the Sheet privately.
Lands in T7.
"""

# Filled in T7.
def sweep_misses() -> None:
    """Post one escalation message per missing person per week (idempotent)."""
    raise NotImplementedError("Escalation lands in T7 (blocked by H6, H7).")
