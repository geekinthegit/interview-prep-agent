"""Section splitting and anchors. The Markdown below is synthetic test input, not research data."""

from prep_agent.sections import build_index, github_slug, split_markdown


def test_github_slug():
    assert github_slug("2.3.5 Sample Size Rationale") == "235-sample-size-rationale"
    assert github_slug("6.2 Estimation and uncertainty of Δκ") == "62-estimation-and-uncertainty-of-δκ"
    assert github_slug("[6. Analysis](decisions/06-analysis.md)") == "6-analysis"
    assert github_slug("baseline — analysis n = 300") == "baseline--analysis-n--300"
    assert github_slug("13. AI/tool division of labor") == "13-aitool-division-of-labor"
    assert github_slug("definition_replacement — x") == "definition_replacement--x"


SYNTHETIC = """preamble without heading
# Title
intro
## Part
body
#### Deep
deep body
## Part
second
```
## not a heading
```
### Sub
sub body
"""


def test_split_markdown_levels_duplicates_and_fences():
    sections = split_markdown("source_docs/x.md", SYNTHETIC)
    assert [s.anchor for s in sections] == ["title", "part", "deep", "part-1", "sub"]
    part = sections[1]
    assert "#### Deep" in part.text and "deep body" in part.text
    assert "## not a heading" in sections[3].text
    assert all("preamble" not in s.text for s in sections)
    assert sections[0].location == "source_docs/x.md#title"


def test_sections_include_subsections():
    title, part, deep, part1, sub = split_markdown("source_docs/x.md", SYNTHETIC)
    assert "second" in title.text and "sub body" in title.text  # level 1 runs to the end
    assert "second" not in part.text  # ends at the next ## heading
    assert deep.text == "#### Deep\ndeep body"
    assert "### Sub" in part1.text and "sub body" in part1.text
    assert part.contains(deep) and title.contains(sub) and not part.contains(part1)
    assert deep.overlaps(part) and not deep.overlaps(sub)


def test_duplicate_counter_includes_deeper_headings():
    sections = split_markdown("source_docs/x.md", "# A\n##### Same\n## Same\n")
    assert [s.anchor for s in sections] == ["a", "same-1"]


def test_real_index_matches_decision_log_links():
    """Spot check against anchors that DECISIONS.md itself links to."""
    locations = {s.location for s in build_index()}
    for loc in [
        "source_docs/decisions/02-3-sampling-design.md#237-paired-resampling-for-uncertainty-estimation",
        "source_docs/decisions/06-analysis.md#62-estimation-and-uncertainty-of-δκ",
        "source_docs/decisions/06-analysis.md#621-bootstrap-specification",
        "source_docs/docs/research-workflow.md#stage-2-develop-and-validate-the-computational-instrument",
    ]:
        assert loc in locations
