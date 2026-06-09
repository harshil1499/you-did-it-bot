"""Timezone-aware scheduling logic.

Pure functions (no Slack, no Sheets) so they unit-test without tokens. "Is this
person due now?" and the week_of key land in T6.
"""

# Filled in T6.
def is_due_now(timezone: str, now_utc, day: str, hour_local: int) -> bool:
    """True if it's `day` at `hour_local` in the person's timezone right now."""
    raise NotImplementedError("Scheduling logic lands in T6.")


def week_of(timezone: str, now_utc) -> str:
    """Monday-of-current-week date (in the person's tz) as an ISO string. The key everywhere."""
    raise NotImplementedError("Scheduling logic lands in T6.")
