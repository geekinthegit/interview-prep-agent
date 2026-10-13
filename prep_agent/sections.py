"""Section index of source_docs/ (spec: Sections and retrieval).

Each Markdown file is split at headings of level 1-4. A section runs from its
heading to the next heading of the same or a higher level, so it includes its
subsections; a section and its subsections are all indexed. Anchors follow
GitHub's heading-anchor rule. Duplicate anchors in one file are numbered over
all heading levels, as GitHub does.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "source_docs"

# spec: "Each source document is split at Markdown headings (#, ##, ###, ####)."
INDEX_MAX_LEVEL = 4

_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*(?:#+[ \t]*)?$")
_FENCE_RE = re.compile(r"^[ \t]{0,3}(```|~~~)")
_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_HTML_TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class Section:
    path: str  # repository-root relative, e.g. "source_docs/decisions/06-analysis.md"
    anchor: str
    title: str
    level: int
    text: str  # heading line and body, including subsections
    start: int | None = None  # line range [start, end) in the document
    end: int | None = None

    @property
    def location(self) -> str:
        return f"{self.path}#{self.anchor}"

    def contains(self, other: "Section") -> bool:
        """True if other is this section or one of its subsections."""
        if None in (self.start, self.end, other.start, other.end):
            return False
        return (self.path == other.path
                and self.start <= other.start and other.end <= self.end)

    def overlaps(self, other: "Section") -> bool:
        return self.contains(other) or other.contains(self)


def github_slug(title: str) -> str:
    """Anchor GitHub generates for a heading (without the duplicate suffix)."""
    text = _LINK_RE.sub(r"\1", title)
    text = _HTML_TAG_RE.sub("", text)
    text = text.strip().lower()
    kept = [
        ch for ch in text
        if ch in " -_" or unicodedata.category(ch)[0] in "LNM"
    ]
    return "".join(kept).replace(" ", "-")


def split_markdown(path: str, content: str) -> list[Section]:
    """Split one Markdown document into indexed sections, in document order.

    Text before the first heading has no anchor and is not indexed.
    """
    lines = content.splitlines()
    headings = []  # (line number, level, title, anchor) for every heading
    seen: dict[str, int] = {}
    in_fence = False
    for i, line in enumerate(lines):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        match = None if in_fence else _HEADING_RE.match(line)
        if not match:
            continue
        title = match.group(2)
        slug = github_slug(title)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchor = slug if count == 0 else f"{slug}-{count}"
        headings.append((i, len(match.group(1)), title, anchor))

    sections = []
    for n, (start, level, title, anchor) in enumerate(headings):
        if level > INDEX_MAX_LEVEL:
            continue
        end = next((h[0] for h in headings[n + 1:] if h[1] <= level), len(lines))
        sections.append(Section(
            path=path, anchor=anchor, title=title, level=level,
            text="\n".join(lines[start:end]).strip(), start=start, end=end,
        ))
    return sections


def document_paths() -> list[str]:
    """Repository-root relative paths of all Markdown source documents."""
    return sorted(
        p.relative_to(REPO_ROOT).as_posix() for p in SOURCE_DIR.rglob("*.md")
    )


def build_index() -> list[Section]:
    sections: list[Section] = []
    for path in document_paths():
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        sections.extend(split_markdown(path, content))
    return sections


def index_by_location(sections: list[Section]) -> dict[str, Section]:
    return {s.location: s for s in sections}
