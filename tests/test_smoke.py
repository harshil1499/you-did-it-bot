"""Skeleton smoke tests. No tokens, no network: sets dummy env, then checks the
HTTP surface and the event-dedup logic boot and behave."""

import os

# Dummy required env so config.validate_required() passes and the app imports.
os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test")
os.environ.setdefault("SLACK_SIGNING_SECRET", "test-secret")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("SCHEDULER_SECRET", "scheduler-test")

import app  # noqa: E402


def _client():
    app.flask_app.config.update(TESTING=True)
    return app.flask_app.test_client()


def test_health_ok():
    assert _client().get("/health").status_code == 200


def test_task_endpoint_requires_secret():
    c = _client()
    assert c.post("/tasks/run-checkins").status_code == 401
    ok = c.post(
        "/tasks/run-checkins", headers={"X-Scheduler-Secret": "scheduler-test"}
    )
    assert ok.status_code == 200


def test_event_dedup():
    assert app._already_processed("evt-1") is False
    assert app._already_processed("evt-1") is True  # second delivery is a repeat
    assert app._already_processed(None) is False  # missing id never dedups
