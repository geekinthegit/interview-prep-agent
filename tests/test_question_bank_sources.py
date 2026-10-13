"""Every source location in question_bank.md must exist in the section index (spec: Rules for the agent)."""

import pytest

from prep_agent.questions import load_question_bank
from prep_agent.sections import build_index, index_by_location

QUESTIONS = load_question_bank()
BY_LOCATION = index_by_location(build_index())


def test_question_bank_has_12_questions():
    assert [q.qid for q in QUESTIONS] == [f"Q{i:02d}" for i in range(1, 13)]


@pytest.mark.parametrize(
    "qid,location",
    [(q.qid, loc) for q in QUESTIONS for loc in q.sources],
)
def test_source_location_is_indexed(qid, location):
    assert location in BY_LOCATION, f"{qid}: {location} is not in the section index"
