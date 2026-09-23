"""Query-time expansion from everyday data-protection-officer vocabulary to
statutory terminology.

The GDPR and BDSG use precise legal terms: "Verletzung des Schutzes
personenbezogener Daten" where practitioners say "Datenpanne" or
"Datenleck", "Auftragsverarbeitung" where a colloquial question might say
"outsourcing", and so on. A pure TF-IDF match on the statutory text alone
would miss a query phrased the way a DSB actually talks. This module adds
the statutory vocabulary alongside the colloquial term in the query before
it reaches the vectorizer; it never touches the indexed corpus, so every
citation returned still points at the unmodified official text.

The list is curated from recurring terminology in day-to-day DSB practice,
not exhaustive, and is meant to be extended as gaps are found.
"""

from __future__ import annotations

import re

_SYNONYMS: dict[str, str] = {
    "datenpanne": "verletzung des schutzes personenbezogener daten meldepflicht",
    "datenleck": "verletzung des schutzes personenbezogener daten",
    "datenschutzverletzung": "verletzung des schutzes personenbezogener daten",
    "loeschantrag": "recht auf loeschung",
    "loeschungsantrag": "recht auf loeschung",
    "auskunftsanspruch": "auskunftsrecht",
    "auskunftsantrag": "auskunftsrecht der betroffenen person",
    "kamera": "videoueberwachung",
    "kameraueberwachung": "videoueberwachung",
    "mitarbeiterdaten": "beschaeftigtendatenschutz datenverarbeitung fuer zwecke des beschaeftigungsverhaeltnisses",
    "personalakte": "beschaeftigtendatenschutz",
    "dsfa": "datenschutz folgenabschaetzung",
    "folgenabschaetzung": "datenschutz folgenabschaetzung",
    "outsourcing": "auftragsverarbeitung auftragsverarbeiter",
    "dienstleister": "auftragsverarbeiter",
    "cookie": "einwilligung",
    "cookies": "einwilligung",
    "einwilligungserklaerung": "einwilligung",
    "bussgeld": "geldbusse",
    "strafe": "geldbusse strafvorschriften",
    "loeschfrist": "speicherbegrenzung recht auf loeschung",
    "aufbewahrungsfrist": "speicherbegrenzung",
    "dsb": "datenschutzbeauftragte datenschutzbeauftragter",
    "datenschutzbeauftragten": "datenschutzbeauftragte datenschutzbeauftragter benennung",
    "bestellt": "benannt benennung",
    "bestellen": "benennen benennung",
    "bestellung": "benennung benennen",
    "bestellpflicht": "benennungspflicht benennung",
}

_WORD_RE = re.compile(r"[a-zäöüß]+")


def expand_query(query: str, normalize) -> str:
    """Returns the query with statutory synonyms appended for any recognised
    colloquial term. `normalize` is the same normalize_de function used by
    the vectorizer, applied here so lookups are umlaut-insensitive too."""
    normalized = normalize(query)
    words = _WORD_RE.findall(normalized)
    additions = [expansion for word in words if (expansion := _SYNONYMS.get(word))]
    if not additions:
        return query
    return query + " " + " ".join(additions)
