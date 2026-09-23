"""Tokenises and stems German text for TF-IDF, so that inflected forms of the
same word count as the same term.

German legal and everyday language differ mainly by inflection: the statute
says "Datenschutzbeauftragte oder einen Datenschutzbeauftragten" while a
question says "Datenschutzbeauftragter", and "benennen" appears as
"benennt", "benannt" or "Benennung" depending on where in a sentence it
falls. Plain TF-IDF treats every one of these as an unrelated token. The
NLTK Snowball stemmer for German (a pure suffix-stripping algorithm, not a
downloaded model or corpus) reduces most of that variation to a shared stem,
so "Datenschutzbeauftragter" and "Datenschutzbeauftragten" both become
"datenschutzbeauftragt" and match each other.

Stemming does not bridge genuine synonyms between different words, such as
"bestellen" and "benennen" for appointing a DPO; that is handled separately
by the curated expansion in synonyms_de.py, applied to the query before it
reaches this analyzer.
"""

from __future__ import annotations

import re

from nltk.stem.snowball import SnowballStemmer

from .text_normalize import normalize_de

_STEMMER = SnowballStemmer("german")
_TOKEN_RE = re.compile(r"[a-z]+")


def stem(word: str) -> str:
    return _STEMMER.stem(word)


def tokenize_and_stem(text: str) -> list[str]:
    normalized = normalize_de(text)
    return [stem(t) for t in _TOKEN_RE.findall(normalized)]


class GermanAnalyzer:
    """Callable usable as TfidfVectorizer(analyzer=...). Passing a custom
    analyzer makes scikit-learn ignore its own preprocessor, tokenizer,
    stop_words and ngram_range arguments, so all of that logic is reproduced
    here explicitly.

    Implemented as a class rather than a closure so that a fitted
    TfidfVectorizer using it can still be pickled: pickle stores a plain
    function by its module-level qualified name, which a nested closure does
    not have, but it stores a class instance by its (picklable) state.
    """

    def __init__(self, stopwords_stemmed: frozenset[str], ngram_range: tuple[int, int] = (1, 2)):
        self.stopwords_stemmed = stopwords_stemmed
        self.ngram_range = ngram_range

    def __call__(self, text: str) -> list[str]:
        min_n, max_n = self.ngram_range
        tokens = [
            t for t in tokenize_and_stem(text)
            if len(t) > 1 and t not in self.stopwords_stemmed
        ]
        grams: list[str] = []
        for n in range(min_n, max_n + 1):
            for i in range(len(tokens) - n + 1):
                grams.append(" ".join(tokens[i : i + n]))
        return grams
