"""API key handling and an app smoke test. No request is sent: no key is set in these tests."""

import pytest
from streamlit.testing.v1 import AppTest

from prep_agent import llm


def test_client_ignores_openai_api_key(monkeypatch):
    monkeypatch.delenv(llm.API_KEY_ENV, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-should-not-be-used")
    with pytest.raises(llm.MissingKeyError):
        llm.make_client()


def test_client_uses_ablation_key_without_retries(monkeypatch):
    monkeypatch.setenv(llm.API_KEY_ENV, "sk-test-placeholder")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-should-not-be-used")
    client = llm.make_client()  # constructing the client sends no request
    assert client.api_key == "sk-test-placeholder"
    assert client.max_retries == 0


def _button(at, label):
    return next(b for b in at.button if b.label == label)


def test_app_flow_without_key_sends_no_request(monkeypatch):
    monkeypatch.delenv(llm.API_KEY_ENV, raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = AppTest.from_file("../app.py", default_timeout=30).run()
    assert not at.exception
    _button(at, "Start session").click().run()
    _button(at, "Next question").click().run()
    assert "Why did you sample 300 utterances?" in at.markdown[0].value
    # The source location stays hidden until the user answers.
    assert not any("02-3-sampling-design" in m.value for m in at.markdown)
    at.chat_input[0].set_value("Because of resource constraints.").run()
    assert not at.exception
    assert at.session_state.api_calls == 0
    assert any("No request was sent" in e.value for e in at.error)
    assert any("02-3-sampling-design.md#235-sample-size-rationale" in c.value for c in at.caption)


def test_app_flow_with_mocked_model(monkeypatch):
    """MOCK: the model functions are replaced by canned synthetic outputs; no request is sent."""
    from prep_agent.prompts import CONSISTENT, NOT_IN_RECORD

    calls = []
    loc = "source_docs/decisions/02-3-sampling-design.md#235-sample-size-rationale"

    def fake_check(client, question, answer, sources, retrieved, boundaries, allow_follow_up):
        calls.append(allow_follow_up)
        output = {"answer_language": "English", "feedback": "synthetic feedback",
                  "claims": [{"claim": "c1", "label": CONSISTENT, "source_locations": [loc],
                              "boundary_id": None, "explanation": "e"},
                             {"claim": "c2", "label": NOT_IN_RECORD, "source_locations": [],
                              "boundary_id": "R5", "explanation": "e"}]}
        if allow_follow_up:
            output.update(follow_up_question="synthetic follow-up?", follow_up_source_locations=[loc])
        return {"response_id": "mock", "output": output}

    monkeypatch.setattr(llm, "make_client", lambda: object())
    monkeypatch.setattr(llm, "check_answer", fake_check)
    at = AppTest.from_file("../app.py", default_timeout=30).run()
    _button(at, "Start session").click().run()
    _button(at, "Next question").click().run()
    at.chat_input[0].set_value("Resource constraints.").run()
    assert at.session_state.api_calls == 1
    assert any("synthetic follow-up?" in m.value for m in at.markdown)
    at.run()  # a plain rerun must not send the request again
    assert at.session_state.api_calls == 1 and calls == [True]
    at.chat_input[0].set_value("Follow-up answer.").run()
    assert at.session_state.api_calls == 2 and calls == [True, False]
    assert at.session_state.turns[0]["phase"] == "done"
    _button(at, "End session").click().run()
    assert not at.exception
    page = "\n".join(m.value for m in at.markdown)
    assert "Sections to reread" in page
    assert "#prespecified-boundaries" in page  # boundary R5 was cited
