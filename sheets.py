"""Google Sheets persistence (Application Default Credentials, no key file).

The Cloud Run service runs as a Venice-controlled service account; gspread uses
the ambient identity. Venice shares the Sheet with that SA and injects
GOOGLE_SHEET_ID. Tabs and idempotent writes land in T5.
"""

# Filled in T5.
def read_roster() -> list[dict]:
    """Read the Roster tab: name, slack_user_id, timezone, active."""
    raise NotImplementedError("Sheet persistence lands in T5 (blocked by H4).")


def append_checkin(**row) -> None:
    """Idempotent write to the Checkins tab, keyed by slack_user_id + week_of + task_number."""
    raise NotImplementedError("Sheet persistence lands in T5 (blocked by H4).")
