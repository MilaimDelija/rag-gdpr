"""TF-IDF retrieval over the legal corpus.

A dedicated vector database is unwarranted for a corpus of a few hundred
paragraphs: a TF-IDF matrix with cosine similarity fits comfortably in memory,
requires no model download, and is, for retrieval over short legal
provisions rich in distinctive terminology, competitive with dense embeddings
because the terms that make two passages relevant to the same query, such as
"Löschung" or "Einwilligung", are exactly the terms TF-IDF weights highest.
"""

from __future__ import annotations

import pickle
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .analyzer_de import GermanAnalyzer
from .chunks import Chunk, load_all_chunks
from .stopwords_de import GERMAN_STOPWORDS_STEMMED
from .synonyms_de import expand_query
from .text_normalize import normalize_de

INDEX_PATH = Path(__file__).parent / "corpus" / "processed" / "index.pkl"


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


def build_index(chunks: list[Chunk] | None = None, index_path: Path | str = INDEX_PATH) -> None:
    chunks = chunks if chunks is not None else load_all_chunks()
    vectorizer = TfidfVectorizer(
        analyzer=GermanAnalyzer(GERMAN_STOPWORDS_STEMMED, ngram_range=(1, 2)),
        min_df=1,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform([c.text for c in chunks])
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}, f)


_DEFINITION_TERM_RE = re.compile(r"„([^“]+)“")
_STRIP_ARTICLE_RE = re.compile(r"^(ein|eine|einer|eines|der|die|das)\s+", re.IGNORECASE)
_DEFINITION_QUERY_PATTERNS = [
    re.compile(r"^\s*was\s+(?:ist|sind|bedeutet|hei(?:ss|ß)t)\s+(.*?)\s*\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*wie\s+(?:ist|sind)\s+(.*?)\s+definiert\s*\??\s*$", re.IGNORECASE),
    re.compile(r"^\s*definition\s+(?:von|der|des)\s+(.*?)\s*\??\s*$", re.IGNORECASE),
]


class Retriever:
    def __init__(self, index_path: Path | str = INDEX_PATH):
        with open(index_path, "rb") as f:
            state = pickle.load(f)
        self.vectorizer: TfidfVectorizer = state["vectorizer"]
        self.matrix = state["matrix"]
        self.chunks: list[Chunk] = state["chunks"]
        self._definitions = self._build_definition_lookup()

    def _build_definition_lookup(self) -> dict[str, Chunk]:
        """Maps the normalised defined term of every Art. 4 DSGVO entry (e.g.
        "auftragsverarbeiter") to its chunk, so a direct "was ist X" question
        can resolve straight to its statutory definition even when X is too
        common a word elsewhere in the corpus for TF-IDF alone to rank it
        first."""
        lookup: dict[str, Chunk] = {}
        for chunk in self.chunks:
            if chunk.source == "dsgvo" and "Art. 4 Nr." in chunk.citation:
                m = _DEFINITION_TERM_RE.search(chunk.text)
                if m:
                    lookup[normalize_de(m.group(1))] = chunk
        return lookup

    def _definition_lookup(self, query: str) -> RetrievedChunk | None:
        stripped = query.strip()
        term = None
        for pattern in _DEFINITION_QUERY_PATTERNS:
            m = pattern.match(stripped)
            if m:
                term = _STRIP_ARTICLE_RE.sub("", m.group(1)).strip()
                break
        if not term:
            return None
        normalized = normalize_de(term)
        chunk = self._definitions.get(normalized)
        if chunk is None:
            # Loose fallback: a query term that is a substring of, or
            # contains, a defined term (plurals, compounds).
            for defined_term, candidate in self._definitions.items():
                if normalized in defined_term or defined_term in normalized:
                    chunk = candidate
                    break
        return RetrievedChunk(chunk=chunk, score=1.0) if chunk else None

    def search(self, query: str, k: int = 5, source: str | None = None) -> list[RetrievedChunk]:
        if not query.strip():
            return []
        results: list[RetrievedChunk] = []
        seen_ids: set[str] = set()

        direct_hit = self._definition_lookup(query)
        if direct_hit and (source is None or direct_hit.chunk.source == source):
            results.append(direct_hit)
            seen_ids.add(direct_hit.chunk.id)

        expanded = expand_query(query, normalize_de)
        query_vec = self.vectorizer.transform([expanded])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        ranked_idx = scores.argsort()[::-1]
        for idx in ranked_idx:
            if scores[idx] <= 0:
                break
            chunk = self.chunks[idx]
            if chunk.id in seen_ids:
                continue
            if source and chunk.source != source:
                continue
            results.append(RetrievedChunk(chunk=chunk, score=float(scores[idx])))
            if len(results) >= k:
                break
        return results[:k]

    def get(self, chunk_id: str) -> Chunk | None:
        for c in self.chunks:
            if c.id == chunk_id:
                return c
        return None


if __name__ == "__main__":
    build_index()
    print(f"Index geschrieben nach {INDEX_PATH}")
