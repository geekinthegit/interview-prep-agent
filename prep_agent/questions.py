"""Fixed question bank, generated-question candidates, and claim boundaries."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

from .sections import REPO_ROOT, Section

QUESTION_BANK_PATH = REPO_ROOT / "question_bank.md"
SOURCE_SEPARATOR = " ; "

SCORING_RECORD_PATH = "source_docs/reports/main-scoring-record-2026-09-24.md"
BOUNDARY_SECTION_ANCHOR = "12-interpretation-boundaries"

_ROW_RE = re.compile(r"^\|\s*(Q\d+)\s*\|(.*)\|(.*)\|\s*$")
_BOUNDARY_RE = re.compile(r"^- ([A-Z]+\d+)\.\s+(.*)$")
_LINK_ITEM_RE = re.compile(r"^\s*- \[")

# A generated question needs a section with enough prose to ask about.
MIN_GENERATION_CHARS = 300


@dataclass
class Question:
    qid: str  # "Q01" for fixed questions, "G1", "G2", ... for generated ones
    text: str
    sources: list[str] = field(default_factory=list)
    kind: str = "fixed"  # "fixed" or "generated"


@dataclass(frozen=True)
class Boundary:
    bid: str
    text: str
    location: str  # the indexed section that contains the statement


def load_question_bank(path=QUESTION_BANK_PATH) -> list[Question]:
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _ROW_RE.match(line)
        if not match:
            continue
        qid, text, sources = match.groups()
        locations = [s.strip() for s in sources.strip().split(SOURCE_SEPARATOR.strip())]
        questions.append(Question(qid=qid, text=text.strip(),
                                  sources=[s for s in locations if s]))
    return questions


def in_scope(location: str, scope: str | None) -> bool:
    """scope is None for all documents, otherwise one document path."""
    return scope is None or location.split("#", 1)[0] == scope


def fixed_questions_in_scope(questions: list[Question], scope: str | None) -> list[Question]:
    return [q for q in questions if any(in_scope(s, scope) for s in q.sources)]


def _is_link_list(section: Section) -> bool:
    body = [l for l in section.text.splitlines()[1:] if l.strip()]
    if not body:
        return True
    return sum(bool(_LINK_ITEM_RE.match(l)) for l in body) > len(body) / 2


def generation_candidates(sections: list[Section], scope: str | None,
                          exclude: set[str]) -> list[Section]:
    """Sections a generated question may be drawn from."""
    return [
        s for s in sections
        if in_scope(s.location, scope)
        and s.location not in exclude
        and len(s.text) >= MIN_GENERATION_CHARS
        and not _is_link_list(s)
    ]


def pick_generation_section(sections: list[Section], scope: str | None,
                            exclude: set[str], rng: random.Random) -> Section | None:
    candidates = generation_candidates(sections, scope, exclude)
    return rng.choice(candidates) if candidates else None


def load_boundaries(sections: list[Section]) -> list[Boundary]:
    """Claim boundary statements in section 12 of the main scoring record.

    Section 12 includes its subsections, so each statement appears in more than
    one indexed section. Each statement is listed once, in document order, with
    the location of the innermost section that contains it.
    """
    record = [s for s in sections if s.path == SCORING_RECORD_PATH]
    top = next((s for s in record if s.anchor == BOUNDARY_SECTION_ANCHOR), None)
    if top is None:
        return []
    found: dict[str, Boundary] = {}
    for section in (s for s in record if top.contains(s)):  # document order, parents first
        for line in section.text.splitlines():
            match = _BOUNDARY_RE.match(line.strip())
            if match:
                bid = match.group(1)
                found[bid] = Boundary(bid=bid, text=match.group(2), location=section.location)
    return list(found.values())
