"""Keyword search, boundaries, output validation. Sections and outputs here are synthetic unless noted."""

from prep_agent.prompts import CONSISTENT, INCONSISTENT, NOT_IN_RECORD, check_schema
from prep_agent.questions import fixed_questions_in_scope, load_boundaries, load_question_bank
from prep_agent.retrieval import KeywordIndex
from prep_agent.sections import Section, build_index, split_markdown
from prep_agent.session import build_check_context, sections_to_reread, validate_check_output


def _s(anchor, text):
    return Section(path="source_docs/x.md", anchor=anchor, title=anchor, level=2, text=text)


SYN = [_s("a", "## a\nbootstrap resampling of utterances"),
       _s("b", "## b\ntranscript cluster design"),
       _s("c", "## c\nplaceholder token count"),
       _s("d", "## d\nnothing relevant here"),
       _s("e", "## e\nbootstrap bootstrap transcript")]


def test_search_excludes_sources_and_returns_top3_positive():
    idx = KeywordIndex(SYN)
    hits = idx.search("bootstrap transcript placeholder", exclude=[SYN[0]])
    locs = [s.location for s, _ in hits]
    assert "source_docs/x.md#a" not in locs
    assert len(locs) == 3 and "source_docs/x.md#d" not in locs


NESTED = split_markdown("source_docs/y.md", """# Doc
## Bootstrap
bootstrap resampling
### Bootstrap seed
bootstrap seed bootstrap
## Placeholder
placeholder tokens
## Other
bootstrap note
""")


def test_search_skips_parent_and_child_of_selected_or_source_sections():
    by_anchor = {s.anchor: s for s in NESTED}
    idx = KeywordIndex(NESTED)
    ranked_all = [s.anchor for s, _ in idx.search("bootstrap seed", exclude=[], k=len(NESTED))]
    taken = [s.anchor for s, _ in idx.search("bootstrap seed", exclude=[])]
    # Each selected match is distinct text: no selected section contains another.
    chosen = [by_anchor[a] for a in taken]
    assert all(not a.overlaps(b) for i, a in enumerate(chosen) for b in chosen[i + 1:])
    assert taken[0] == ranked_all[0]
    # A source section blocks its parent and its subsections.
    with_source = [s.anchor for s, _ in idx.search("bootstrap seed", exclude=[by_anchor["bootstrap"]])]
    assert not {"doc", "bootstrap", "bootstrap-seed"} & set(with_source)
    assert "other" in with_source


def test_no_match_uses_source_sections_only():
    by_loc = {s.location: s for s in SYN}
    ctx = build_check_context(["source_docs/x.md#a", "source_docs/x.md#zzz"], "완전히 다른 언어",
                              by_loc, KeywordIndex(SYN))
    assert ctx["source_sections"] == ["source_docs/x.md#a"]
    assert ctx["missing_sources"] == ["source_docs/x.md#zzz"]
    assert ctx["retrieved_sections"] == []


def test_boundaries_from_real_scoring_record():
    boundaries = load_boundaries(build_index())
    ids = [b.bid for b in boundaries]
    assert ids == ["C1", "C2", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "U6", "U11", "P1"]
    loc = {b.bid: b.location.split("#")[1] for b in boundaries}
    assert loc["R5"] == "prespecified-boundaries" and loc["P1"] == "post-result-reporting-restriction"


def test_scope_filter_on_real_bank():
    pool = fixed_questions_in_scope(load_question_bank(), "source_docs/AI_WORKFLOW.md")
    assert [q.qid for q in pool] == ["Q10"]


def test_schema_restricts_locations_and_follow_up():
    schema = check_schema(["L1", "L2"], ["C1"], allow_follow_up=False)
    claim = schema["properties"]["claims"]["items"]
    assert claim["properties"]["source_locations"]["items"]["enum"] == ["L1", "L2"]
    assert "follow_up_question" not in schema["properties"]
    assert "follow_up_question" in check_schema(["L1"], ["C1"], True)["required"]


def test_validate_check_output_flags_problems():
    output = {"claims": [
        {"label": CONSISTENT, "source_locations": [], "boundary_id": None},
        {"label": INCONSISTENT, "source_locations": ["L9"], "boundary_id": None},
        {"label": CONSISTENT, "source_locations": ["L1"], "boundary_id": "C1"},
        {"label": NOT_IN_RECORD, "source_locations": [], "boundary_id": "R5"},
    ]}
    problems = validate_check_output(output, ["L1"], ["C1", "R5"])
    assert len(problems) == 4  # claim 1 no source, claim 2 bad location + no source, claim 3 boundary label


def test_sections_to_reread():
    exchanges = [{
        "context": {"source_sections": ["S1"]},
        "output": {"claims": [
            {"label": INCONSISTENT, "source_locations": ["S2"], "boundary_id": None},
            {"label": NOT_IN_RECORD, "source_locations": [], "boundary_id": "R5"},
        ]},
    }, {"context": {"source_sections": ["S3"]},
        "output": {"claims": [{"label": CONSISTENT, "source_locations": ["S3"], "boundary_id": None}]}}]
    assert sections_to_reread(exchanges, {"R5": "B12"}) == ["S1", "S2", "B12"]
