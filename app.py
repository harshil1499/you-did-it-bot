"""you-did-it-bot HTTP service.

One web service, one container, deployed by the platform partner on Cloud Run. Slack delivers
events via Events API over HTTP (not Socket Mode, per H1). This module owns the
HTTP surface: the Slack events endpoint, the health check, and the Cloud Scheduler
task endpoints. The actual behavior (conversation, coaching, persistence,
escalation) lives in the other modules and is wired in as those bits land.
"""

from __future__ import annotations

import logging
import threading
import time

from flask import Flask, request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

import config

logging.basicConfig(level=logging.INFO)
# Never log full task/metric text in production (Cloud Run retains logs); log
# identifiers and outcomes only.
log = logging.getLogger("you-did-it-bot")

config.validate_required()

bolt_app = App(
    token=config.SLACK_BOT_TOKEN,
    signing_secret=config.SLACK_SIGNING_SECRET,
    # Bolt verifies the Slack request signature for us using the signing secret.
    # Skip the auth.test network call at startup so the service boots
    # deterministically (and offline in tests); the token is exercised on first use.
    token_verification_enabled=False,
)
handler = SlackRequestHandler(bolt_app)
flask_app = Flask(__name__)


# --- Event de-duplication -----------------------------------------------------
# Slack retries delivery, so the same event_id can arrive more than once. A small
# in-memory TTL set is enough at ~25 DMs/week, single instance. Durable, against
# duplicates that survive a restart, comes from idempotent Sheet writes (T4/T5).
_SEEN_TTL_SECONDS = 600
_seen_events: dict[str, float] = {}
_seen_lock = threading.Lock()


def _already_processed(event_id: str | None) -> bool:
    if not event_id:
        return False
    now = time.time()
    with _seen_lock:
        for eid, ts in list(_seen_events.items()):
            if now - ts > _SEEN_TTL_SECONDS:
                del _seen_events[eid]
        if event_id in _seen_events:
            return True
        _seen_events[event_id] = now
        return False


def _run_async(fn, *args, **kwargs):
    """Run slow work off the request thread so we satisfy Slack's 3-second rule."""
    threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()


# --- Slack events -------------------------------------------------------------
@bolt_app.event("message")
def on_message(event, ack):
    # ack immediately; real work happens in a background thread (T2/T3 fill this in).
    ack()
    if event.get("channel_type") != "im" or event.get("bot_id"):
        return
    _run_async(_handle_dm, event)


def _handle_dm(event):
    """Placeholder for the DM check-in + coaching loop (T2/T3)."""
    user = event.get("user")
    log.info("DM received from user=%s (handler not yet implemented)", user)


@flask_app.post("/slack/events")
def slack_events():
    # Bolt answers url_verification and signature checks inside the handler.
    payload = request.get_json(silent=True) or {}
    if _already_processed(payload.get("event_id")):
        return "", 200
    return handler.handle(request)


# --- Health -------------------------------------------------------------------
@flask_app.get("/health")
def health():
    return "OK", 200


# --- Cloud Scheduler task endpoints (guarded by a shared secret) --------------
def _scheduler_authorized() -> bool:
    return request.headers.get("X-Scheduler-Secret") == config.SCHEDULER_SECRET


@flask_app.post("/tasks/run-checkins")
def run_checkins():
    if not _scheduler_authorized():
        return jsonify(error="unauthorized"), 401
    # T6: for each person whose local time is now Monday 11:00 and who has not
    # been DMed this week, send the opening check-in. Not yet implemented.
    return jsonify(status="ok", action="run-checkins", implemented=False), 200


@flask_app.post("/tasks/sweep-misses")
def sweep_misses():
    if not _scheduler_authorized():
        return jsonify(error="unauthorized"), 401
    # T7: find people past the deadline who haven't completed; post escalation.
    return jsonify(status="ok", action="sweep-misses", implemented=False), 200


@flask_app.post("/tasks/rollup")
def rollup():
    if not _scheduler_authorized():
        return jsonify(error="unauthorized"), 401
    # T8: keep the Sheet's consolidated rollup view current (no Slack post;
    # the president reviews privately in the Sheet).
    return jsonify(status="ok", action="rollup", implemented=False), 200


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=config.PORT)
