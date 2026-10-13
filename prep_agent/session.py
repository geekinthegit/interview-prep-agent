"""Session logic that does not call the model."""

from __future__ import annotations

from .prompts import CONSISTENT, INCONSISTENT, LABELS, NOT_IN_RECORD
from .retrieval import KeywordIndex
from .sections import Section


def resolve_sources(locations: list[str], by_location: dict[str, Section]):
    """Split source locations into indexed sections and locations not in the index."""
    found, missing = [], []
    for loc in dict.fromkeys(locations):
        if loc in by_location:
            found.append(by_location[loc])
        else:
            missing.append(loc)
    return found, missing


def build_check_context(source_locations: list[str], answer: str,
                        by_location: dict[str, Section], keywords: KeywordIndex) -> dict:
    """Sections for one record check: source sections plus the top 3 keyword matches."""
    sources, missing = resolve_sources(source_locations, by_location)
    retrieved = [s for s, _ in keywords.search(answer, sources)]
    return {
        "source_sections": [s.location for s in sources],
        "missing_sources": missing,
        "retrieved_sections": [s.location for s in retrieved],
    }


def validate_check_output(output: dict, allowed_locations: list[str],
                          boundary_ids: list[str]) -> list[str]:
    """Problems in a record-check output. Labels are shown as returned, never changed."""
    allowed = set(allowed_locations)
    problems = []
    for i, claim in enumerate(output.get("claims", []), start=1):
        label = claim.get("label")
        locs = claim.get("source_locations", [])
        if label not in LABELS:
            problems.append(f"Claim {i}: unknown label {label!r}.")
        bad = [l for l in locs if l not in allowed]
        if bad:
            problems.append(f"Claim {i}: location(s) not among the checked sections: {', '.join(bad)}.")
        if label in (CONSISTENT, INCONSISTENT) and not [l for l in locs if l in allowed]:
            problems.append(f"Claim {i}: labeled {label!r} but no source section was cited.")
        bid = claim.get("boundary_id")
        if bid is not None and bid not in boundary_ids:
            problems.append(f"Claim {i}: unknown claim boundary identifier {bid!r}.")
        if bid is not None and label != NOT_IN_RECORD:
            problems.append(f"Claim {i}: cites boundary {bid} but is not labeled {NOT_IN_RECORD!r}.")
    for loc in output.get("follow_up_source_locations", []) or []:
        if loc not in allowed:
            problems.append(f"Follow-up: location not among the checked sections: {loc}.")
    return problems


def label_counts(output: dict | None) -> dict[str, int]:
    counts = {label: 0 for label in LABELS}
    for claim in (output or {}).get("claims", []):
        if claim.get("label") in counts:
            counts[claim["label"]] += 1
    return counts


def sections_to_reread(exchanges: list[dict], boundary_locations: dict[str, str]) -> list[str]:
    """Sections to reread after the session.

    For each answered exchange: the question's source sections when any claim is
    not consistent with the record (or no claim was found), the sections cited by
    inconsistent claims, and the section holding any claim boundary that was cited.
    """
    reread: dict[str, None] = {}
    for ex in exchanges:
        output = ex.get("output")
        if output is None:
            continue
        claims = output.get("claims", [])
        if not claims or any(c.get("label") != CONSISTENT for c in claims):
            reread.update(dict.fromkeys(ex["context"]["source_sections"]))
        for c in claims:
            if c.get("label") == INCONSISTENT:
                reread.update(dict.fromkeys(c.get("source_locations", [])))
            bid = c.get("boundary_id")
            if bid in boundary_locations:
                reread[boundary_locations[bid]] = None
    return list(reread)
