"""OpenAI calls (spec: Model and API).

Every function here that takes a client sends one request. The app counts each
request before it is sent. Automatic client retries are disabled so that the
count equals the number of requests.
"""

from __future__ import annotations

import json
import os

from openai import OpenAI

from . import prompts
from .questions import Boundary
from .sections import Section

MODEL = "gpt-5.5-2026-04-23"
API_KEY_ENV = "OPENAI_API_KEY_ABLATION"


class MissingKeyError(RuntimeError):
    pass


def api_key_available() -> bool:
    return bool(os.environ.get(API_KEY_ENV))


def make_client() -> OpenAI:
    """Client built from OPENAI_API_KEY_ABLATION only. OPENAI_API_KEY is never read."""
    key = os.environ.get(API_KEY_ENV)
    if not key:
        raise MissingKeyError(f"Environment variable {API_KEY_ENV} is not set.")
    return OpenAI(api_key=key, max_retries=0)


def _structured_call(client: OpenAI, instructions: str, input_text: str,
                     name: str, schema: dict) -> dict:
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=input_text,
        text={"format": {"type": "json_schema", "name": name,
                         "schema": schema, "strict": True}},
    )
    return {"response_id": response.id, "output": json.loads(response.output_text)}


def generate_question(client: OpenAI, section: Section) -> dict:
    return _structured_call(
        client,
        prompts.GENERATION_INSTRUCTIONS,
        prompts.build_generation_input(section),
        "generated_question",
        prompts.GENERATION_SCHEMA,
    )


def check_answer(client: OpenAI, question: str, answer: str,
                 question_sources: list[Section], retrieved: list[Section],
                 boundaries: list[Boundary], allow_follow_up: bool) -> dict:
    locations = [s.location for s in question_sources + retrieved]
    return _structured_call(
        client,
        prompts.check_instructions(allow_follow_up),
        prompts.build_check_input(question, answer, question_sources, retrieved, boundaries),
        "record_check",
        prompts.check_schema(locations, [b.bid for b in boundaries], allow_follow_up),
    )
