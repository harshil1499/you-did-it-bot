"""Coaching tests — no API key, no network. A fake client returns canned model
output so we exercise prompt assembly, JSON parsing, and the loop decision."""

import os

os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test")
os.environ.setdefault("SLACK_SIGNING_SECRET", "test-secret")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test")
os.environ.setdefault("SCHEDULER_SECRET", "scheduler-test")

import coaching  # noqa: E402


class _Block:
    def __init__(self, text):
        self.text = text


class _Resp:
    def __init__(self, text):
        self.content = [_Block(text)]


class _FakeClient:
    """Records the call and returns whatever text it was seeded with."""

    def __init__(self, text):
        self._text = text
        self.last_kwargs = None

    @property
    def messages(self):
        return self

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _Resp(self._text)


def test_parse_verdict_plain():
    v = coaching.parse_verdict('{"clean": true, "feedback": "", "suggested_rewrite": ""}')
    assert v["clean"] is True


def test_parse_verdict_with_code_fence():
    raw = '```json\n{"clean": false, "feedback": "no number", "suggested_rewrite": "Add 150 members by 6/20"}\n```'
    v = coaching.parse_verdict(raw)
    assert v["clean"] is False
    assert "150" in v["suggested_rewrite"]


def test_evaluate_item_passes_standard_into_system_prompt():
    client = _FakeClient('{"clean": true, "feedback": "", "suggested_rewrite": ""}')
    v = coaching.evaluate_item("Confirm renewal for 15 whitelisters in June.", client=client)
    assert v["clean"] is True
    # The rubric is embedded in the system prompt.
    assert "SMART" in client.last_kwargs["system"]
    assert client.last_kwargs["messages"][0]["content"].startswith("Confirm renewal")


def test_decide_accept_when_clean():
    assert coaching.decide(0, {"clean": True}) == "accept"


def test_decide_push_back_then_flag_at_cap():
    assert coaching.decide(1, {"clean": False}) == "push_back"
    assert coaching.decide(coaching.MAX_ROUNDS, {"clean": False}) == "accept_with_flag"
