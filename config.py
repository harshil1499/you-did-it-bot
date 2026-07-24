"""Environment configuration for you-did-it-bot.

Every value comes from an environment variable. The platform partner injects the secrets from
Secret Manager at deploy time; nothing is hardcoded or committed. Reading happens
here so the rest of the code never touches os.environ directly.

Validation is lazy on purpose: importing this module never raises, so unit tests
(coaching verdicts, timezone logic) run without any tokens. The HTTP service calls
validate_required() at startup and fails fast if a required secret is missing.
"""

import os

# --- Required for the service to run (fail fast at startup) ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SCHEDULER_SECRET = os.environ.get("SCHEDULER_SECRET")

# --- Injected after handoffs (H4 sheet, H6 channels); optional at boot ---
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
ESCALATION_CHANNEL_ID = os.environ.get("ESCALATION_CHANNEL_ID")
ESCALATION_MENTION_IDS = [
    uid.strip()
    for uid in os.environ.get("ESCALATION_MENTION_IDS", "").split(",")
    if uid.strip()
]

# --- Tunable without a code change ---
PORT = int(os.environ.get("PORT", "8080"))
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
CHECKIN_DAY = os.environ.get("CHECKIN_DAY", "Monday")
CHECKIN_HOUR_LOCAL = int(os.environ.get("CHECKIN_HOUR_LOCAL", "11"))

# Required env vars, by the name the deploy config uses.
_REQUIRED = (
    "SLACK_BOT_TOKEN",
    "SLACK_SIGNING_SECRET",
    "ANTHROPIC_API_KEY",
    "SCHEDULER_SECRET",
)


def validate_required():
    """Raise RuntimeError listing any required env vars that are missing.

    Called once at service startup (app.py), not at import time.
    """
    missing = [name for name in _REQUIRED if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
