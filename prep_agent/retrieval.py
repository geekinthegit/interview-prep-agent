"""Keyword search over the section index (spec: Sections and retrieval).

Scoring is BM25 over word tokens; answers are assumed to be in English. The
record check uses the question's source sections plus the top 3 other sections
with a positive score.

Sections are nested (a section contains its subsections). A candidate that
overlaps a question source section or an already selected match, as its
subsection or its parent section, is skipped and the next-ranked candidate is
taken, so the 3 matches are distinct text.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from .sections import Section

TOP_K = 3
_K1 = 1.5
_B = 0.75

_TOKEN_RE = re.compile(r"[^\W_]+")
_STOPWORDS = frozenset("""
a about above after again all also am an and any are as at be because been before
being below between both but by can could did do does doing done down during each
few for from further had has have having he her here hers him his how i if in into
is it its itself just me more most my myself no nor not now of off on once only or
other our ours out over own same she should so some such than that the their theirs
them then there these they this those through to too under until up very was we
were what when where which while who whom why will with would you your yours
think yes yeah um uh like really actually
""".split())


def tokenize(text: str) -> list[str]:
    tokens = []
    for tok in _TOKEN_RE.findall(text.lower()):
        if tok in _STOPWORDS:
            continue
        if len(tok) < 2 and not tok.isdigit():
            continue
        tokens.append(tok)
    return tokens


class KeywordIndex:
    def __init__(self, sections: list[Section]):
        self.sections = sections
        self._tf = [Counter(tokenize(s.text)) for s in sections]
        self._len = [sum(tf.values()) for tf in self._tf]
        self._avg_len = (sum(self._len) / len(self._len)) if self._len else 0.0
        df = Counter()
        for tf in self._tf:
            df.update(tf.keys())
        n = len(sections)
        self._idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def search(self, query: str, exclude: list[Section], k: int = TOP_K) -> list[tuple[Section, float]]:
        terms = set(tokenize(query))
        scored = []
        for section, tf, length in zip(self.sections, self._tf, self._len):
            score = 0.0
            for term in terms:
                f = tf.get(term, 0)
                if f:
                    norm = f + _K1 * (1 - _B + _B * length / self._avg_len)
                    score += self._idf[term] * f * (_K1 + 1) / norm
            if score > 0:
                scored.append((section, score))
        scored.sort(key=lambda pair: (-pair[1], pair[0].location))
        taken: list[tuple[Section, float]] = []
        for section, score in scored:
            if len(taken) == k:
                break
            blocked = list(exclude) + [t[0] for t in taken]
            if any(section.location == b.location or section.overlaps(b) for b in blocked):
                continue
            taken.append((section, score))
        return taken
