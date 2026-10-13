"""Prompts and output schemas for the two model calls (WORKFLOW 4.3).

1. Question generation from one section (generated questions only).
2. Record check of one answer: claim splitting, labels, feedback, and
   optionally one follow-up question.
"""

from __future__ import annotations

from .questions import Boundary
from .sections import Section

CONSISTENT = "Consistent with the record"
INCONSISTENT = "Inconsistent with the record"
NOT_IN_RECORD = "Not in the record"
LABELS = [CONSISTENT, INCONSISTENT, NOT_IN_RECORD]

NO_GUESSING_RULE = (
    "Use only the text provided in this request. Do not use outside knowledge "
    "about the study, TalkMoves, or the model, and do not fill gaps by guessing. "
    "If the provided sections do not contain what you need, say that it was not "
    "found in the record instead of inferring it."
)


# --- Question generation -------------------------------------------------

GENERATION_INSTRUCTIONS = f"""\
You write questions for a graduate admissions interview about a research study.
The candidate is the researcher who ran the study.

{NO_GUESSING_RULE}

Write exactly one interview question that can be answered fully from the single
section given below. Ask about a decision, a reason, a procedure, or a limitation
stated in that section. Write the question in English. Do not mention the section
title, file name, or section number in the question.

If the section does not contain enough substantive content for an interview
question, set "question" to null and explain why in "reason_if_null".
"""

GENERATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["question", "reason_if_null"],
    "properties": {
        "question": {"type": ["string", "null"]},
        "reason_if_null": {"type": "string"},
    },
}


def build_generation_input(section: Section) -> str:
    return (
        f"Section location: {section.location}\n"
        f"--- SECTION START ---\n{section.text}\n--- SECTION END ---"
    )


# --- Record check --------------------------------------------------------

CHECK_INSTRUCTIONS = f"""\
You check a candidate's interview answer about a research study against the
study's written records, and you give feedback.

{NO_GUESSING_RULE}

Steps:
1. Split the answer into claims. A claim is one statement about the study that
   can be checked against the records (a fact, a decision, a reason, a result,
   or an interpretation). Do not treat greetings, hesitations, or restatements of
   the question as claims. Write each claim in the language of the answer.
2. Label each claim with exactly one of:
   - "{CONSISTENT}": a checked section states the same content. List the
     location(s) of the section(s) that state it.
   - "{INCONSISTENT}": a checked section states different content. List the
     location(s) of the section(s) that state the different content.
   - "{NOT_IN_RECORD}": no checked section states this content. Leave
     source_locations empty. Do not label a claim consistent because it sounds
     plausible; it must be stated in a checked section.
   Only the locations listed under CHECKED SECTIONS may be cited.
3. Claim boundaries: the CLAIM BOUNDARY STATEMENTS restrict what the study
   claims. If a claim goes beyond one of these statements (for example, it
   claims something a statement says is not claimed, or interprets a result in
   a way a statement rules out), label it "{NOT_IN_RECORD}" and set boundary_id
   to that statement's identifier, even if some section seems to support it.
   Otherwise set boundary_id to null.
4. In "explanation", say briefly for each claim what the cited section states,
   or that nothing in the checked sections states it.
5. Write "feedback": a short overall assessment for the candidate, naming what
   was supported, what was wrong, and what was missing compared with the
   question's source sections. Do not add content that is not in the checked
   sections.
{{follow_up_rule}}
Write "explanation", "feedback"{{follow_up_language}} in the same language as the
candidate's answer, and report that language in "answer_language".
If the answer contains no checkable claim, return an empty claims list and say so
in the feedback.
"""

_FOLLOW_UP_RULE = """\
6. Follow-up: you may ask at most one follow-up question. Ask it only about
   content stated in the checked sections, for example a point the answer missed
   or got wrong. List the location(s) it is based on in
   follow_up_source_locations. If no follow-up is useful, set
   follow_up_question to null and follow_up_source_locations to an empty list.
"""


def check_instructions(allow_follow_up: bool) -> str:
    text = CHECK_INSTRUCTIONS.replace(
        "{follow_up_rule}", _FOLLOW_UP_RULE if allow_follow_up else "")
    return text.replace(
        "{follow_up_language}", ', and "follow_up_question"' if allow_follow_up else "")


def check_schema(locations: list[str], boundary_ids: list[str],
                 allow_follow_up: bool) -> dict:
    location_list = {"type": "array", "items": {"type": "string", "enum": locations}}
    boundary = (
        {"anyOf": [{"type": "string", "enum": boundary_ids}, {"type": "null"}]}
        if boundary_ids else {"type": "null"}
    )
    claim = {
        "type": "object",
        "additionalProperties": False,
        "required": ["claim", "label", "source_locations", "boundary_id", "explanation"],
        "properties": {
            "claim": {"type": "string"},
            "label": {"type": "string", "enum": LABELS},
            "source_locations": location_list,
            "boundary_id": boundary,
            "explanation": {"type": "string"},
        },
    }
    properties = {
        "answer_language": {"type": "string"},
        "claims": {"type": "array", "items": claim},
        "feedback": {"type": "string"},
    }
    if allow_follow_up:
        properties["follow_up_question"] = {"type": ["string", "null"]}
        properties["follow_up_source_locations"] = location_list
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(properties),
        "properties": properties,
    }


def build_check_input(question: str, answer: str, question_sources: list[Section],
                      retrieved: list[Section], boundaries: list[Boundary]) -> str:
    parts = [f"QUESTION:\n{question}", f"CANDIDATE ANSWER:\n{answer}", "CHECKED SECTIONS:"]
    for role, sections in (("question source", question_sources),
                           ("keyword match", retrieved)):
        for s in sections:
            parts.append(
                f"--- SECTION START | location: {s.location} | role: {role} ---\n"
                f"{s.text}\n--- SECTION END ---"
            )
    parts.append("CLAIM BOUNDARY STATEMENTS (main scoring record, section 12):")
    parts.extend(f"- {b.bid}. {b.text}" for b in boundaries)
    return "\n\n".join(parts)
