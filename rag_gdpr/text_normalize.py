"""Normalises German spelling variants before TF-IDF tokenisation.

Two independent variants are folded here, both because the two sides of a
retrieval match (the indexed statutory text and a typed query) otherwise
disagree on spelling for reasons that have nothing to do with meaning.

Umlauts: German text can legitimately be typed two ways, "Überwachung" or
its ASCII transliteration "Ueberwachung". A data protection officer typing a
quick query on a keyboard without umlauts, or pasting text from a system
that stripped them, will use the transliterated form even though the
statutory text always uses proper umlauts. Left unhandled, a plain TF-IDF
vectorizer treats "Videoüberwachung" and "Videoueberwachung" as unrelated
tokens and misses an otherwise exact match.

Compound hyphens: official legal text sometimes hyphenates a compound noun
that everyday usage writes as one word, most visibly "Datenschutz-
Folgenabschätzung" in the GDPR itself versus "Datenschutzfolgenabschätzung"
in ordinary usage. Since the tokeniser splits on any non-letter character, a
hyphen with no surrounding whitespace would otherwise turn one compound into
two separate tokens on one side of the match and one token on the other. A
hyphen that does have surrounding whitespace, used as a dash rather than a
compound joiner, is left alone; the tokeniser already splits on that
whitespace regardless.

Kept as a standalone, importable module (rather than an inline lambda)
because scikit-learn pickles a TfidfVectorizer's preprocessor by reference:
unpickling the saved index later requires this function to still be
importable under this exact module path.
"""

from __future__ import annotations

import re

_UMLAUT_MAP = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    "ß": "ss",
}

# A hyphen directly between two letters, e.g. "Datenschutz-Folgenabschätzung",
# is a compound joiner and is removed; "Verantwortliche - oder" (spaced) is
# left untouched since the tokeniser already treats the surrounding
# whitespace as a separator.
_COMPOUND_HYPHEN_RE = re.compile(r"(?<=[a-zäöüßA-ZÄÖÜ])-(?=[a-zäöüßA-ZÄÖÜ])")


def normalize_de(text: str) -> str:
    text = _COMPOUND_HYPHEN_RE.sub("", text)
    text = text.lower()
    for umlaut, ascii_form in _UMLAUT_MAP.items():
        text = text.replace(umlaut.lower(), ascii_form.lower())
    return text
