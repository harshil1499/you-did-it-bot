# you-did-it-bot

A Slack bot that runs a structured weekly check-in with every member of a ~25-person team,
coaches the quality of what they write against an explicit standard, and consolidates clean
results into a single Google Sheet for leadership.

*Built as contract work. The client and the individuals involved are referred to by role here.*

---

## The problem

A growing team needs a weekly check-in, and doing it manually breaks in three separate places:

- **Chasing.** Someone has to notice who hasn't responded and follow up individually. At ~25
  people that quietly consumes a manager's week — and it's the first thing to slip when they get
  busy, which is exactly when visibility matters most.
- **Quality.** Self-reported updates drift toward the vague: *"worked on onboarding," "made
  progress on the integration."* Updates like that can't be acted on, compared week over week, or
  used to spot a project that's actually stuck. The information arrives, but it isn't usable.
- **Consolidation.** Answers land in 25 separate DM threads. Nobody has a single view, so
  leadership either reads everything or reads nothing.

Timezones make all three worse: a distributed team can't share one wall-clock deadline without it
being unfair to someone.

## The solution

A bot that owns the whole loop, not just the reminder:

- **Reaches people on their own clock.** Check-in DMs open Monday 11:00 *local* to each person;
  the deadline lands Tuesday 11:00 local. Scheduling is timezone-aware end to end.
- **Coaches at the point of writing.** Each reported item is evaluated against a written
  standard. If it's too vague, the bot pushes back and asks for a revision — a multi-turn
  ask → revise → re-evaluate loop, capped at 3 rounds so a stubborn item can't spin forever.
- **Has an escape hatch that produces a signal.** Items that still don't meet the standard after
  the cap are stored *flagged as un-coached* rather than dropped or forced through. The failure
  becomes feedback about where the standard itself doesn't work for people.
- **Consolidates automatically.** Clean results are written to a Google Sheet with a rollup view,
  so there's one place to read instead of 25.
- **Chases so a human doesn't.** An hourly sweep escalates missed check-ins to a public channel,
  tagging the company president. Nobody maintains a list of who owes what.

## The value

The design goal is to make quality and accountability *by-products* of the check-in rather than
separate management work:

- **Visibility without chasing** — the follow-up loop runs unattended.
- **Better writing as a side effect** — coaching happens while the person is writing, so there's
  no separate review cycle to staff, and the standard is applied consistently across all ~25
  people instead of depending on which manager reads it.
- **One readable view** — consolidated results instead of scattered threads.
- **A feedback loop on the standard itself** — flagged un-coached items show where the standard
  is failing people, so it can be revised on evidence rather than opinion.

*Status: in active build (see Build status). The above is design intent, not measured outcomes.*

---

## Architecture

One HTTP service in a single container, deployed by the client's platform partner on Google
Cloud Run. Slack delivers events via the **Events API over HTTP** (not Socket Mode). The platform
partner owns the Slack app, secrets, and hosting, and injects all config as environment
variables. This repo owns the bot's logic and never handles raw production tokens.

## Endpoints

- `POST /slack/events` — Slack events + interactivity (acks in <3s, works async).
- `GET /health` — deploy smoke-check and keep-warm.
- `POST /tasks/run-checkins` — hourly; opens the Monday 11:00-local check-in DMs.
- `POST /tasks/sweep-misses` — hourly; escalates misses (no-ops when nobody is due, so the Tuesday-11:00-local deadline lands correctly across timezones).
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

Unit tests run with no tokens and no network: the model client is injectable and config
validation is lazy on purpose, so coaching verdicts and timezone logic are testable offline.

## Build status

- [x] T1 — repo skeleton (Dockerfile, /health, env config, Slack events route, dedup)
- [ ] T2 — DM check-in conversation
- [ ] T3 — coaching loop + writing standard
- [ ] T4 — state reconstruction + idempotency
- [ ] T5 — Sheet persistence
- [ ] T6 — scheduling + timezone logic
- [ ] T7 — miss sweep + escalation
- [ ] T8 — rollup view in the Sheet
- [ ] T9 — live test
- [ ] T10 — harden + compliance
