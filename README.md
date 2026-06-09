# you-did-it-bot

A Slack bot that runs a structured weekly check-in with each team member (~25
people), coaches the quality of what they report against a writing standard, and
stores clean results to a Google Sheet. People who miss the deadline are escalated
to a public channel tagging Kayvon. Kayvon reviews the consolidated results
privately in the Sheet (there is no rollup channel).

## Architecture

One HTTP service in a single container, deployed by Venice Technologies on Google
Cloud Run. Slack delivers events via the **Events API over HTTP** (not Socket
Mode). Venice owns the Slack app, secrets, and hosting and injects all config as
environment variables. This repo owns the bot's logic and never handles raw
production tokens.

Canonical engineering brief: `checkin-bot-setup-todo-harshil.md` (Venice/Jason).

## Endpoints

- `POST /slack/events` — Slack events + interactivity (acks in <3s, works async).
- `GET /health` — deploy smoke-check and keep-warm.
- `POST /tasks/run-checkins` — hourly; opens the Monday 11:00-local check-in DMs.
- `POST /tasks/sweep-misses` — daily; escalates misses.
- `POST /tasks/rollup` — weekly; keeps the Sheet's rollup view current.

All `/tasks/*` endpoints require the `X-Scheduler-Secret` header.

## Run locally

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in for live Slack; not needed for unit tests
pytest
python app.py          # serves on PORT (default 8080)
```

## Build status

- [x] T1 — repo skeleton (Dockerfile, /health, env config, Slack events route, dedup)
- [ ] T2 — DM check-in conversation
- [ ] T3 — coaching loop + writing standard
- [ ] T4 — state reconstruction + idempotency
- [ ] T5 — Sheet persistence (blocked by H4)
- [ ] T6 — scheduling + timezone logic
- [ ] T7 — miss sweep + escalation (blocked by H6, H7)
- [ ] T8 — rollup view in the Sheet
- [ ] T9 — live test (blocked by H8, H9)
- [ ] T10 — harden + compliance
