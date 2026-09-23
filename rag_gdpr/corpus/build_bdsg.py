"""Downloads and parses a curated set of BDSG sections from gesetze-im-internet.de,
the Federal Ministry of Justice's official publication platform for consolidated
federal law texts.

The BDSG has roughly 85 sections spanning supervisory-authority procedure, public-
sector rules and sanctions that are largely outside what a data protection officer
in a private company deals with day to day. Rather than ingest the whole statute at
uneven relevance, this script pulls the subset that recurs in the daily work of a
company DSB: scope, video surveillance, the position and dismissal of the DSB
itself, special categories of data, employee data processing, the statutory
narrowing of the Art. 15-21 GDPR rights, the threshold for appointing an internal
DSB, and the criminal and administrative fine provisions. Each entry in
CURATED_SECTIONS documents why it made the cut, and the produced JSON records that
this is a curated subset rather than the full statute, so downstream tools do not
overstate their coverage.

Run as: python3 -m rag_gdpr.corpus.build_bdsg
Writes: rag_gdpr/corpus/raw/bdsg_<n>.html  (cached per section, one HTTP call each)
        rag_gdpr/corpus/processed/bdsg.json
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

BASE_URL = "https://www.gesetze-im-internet.de/bdsg_2018/__{n}.html"
RAW_DIR = Path(__file__).parent / "raw"
OUT_PATH = Path(__file__).parent / "processed" / "bdsg.json"

CURATED_SECTIONS = {
    1: "Anwendungsbereich - klaert, wann das BDSG neben der DSGVO gilt",
    2: "Begriffsbestimmungen des BDSG - ergaenzt Art4 DSGVO um oeffentliche Stellen des Bundes und der Laender",
    4: "Videoueberwachung oeffentlich zugaenglicher Raeume",
    6: "Stellung der oder des Datenschutzbeauftragten (Kapitel fuer oeffentliche Stellen); Abs4, Abs5 Satz2 und Abs6 gelten ueber die Verweisung in Sec38 Abs2 auch fuer die Datenschutzbeauftragten nicht-oeffentlicher Stellen, insbesondere der Abberufungsschutz in Abs4",
    22: "Verarbeitung besonderer Kategorien personenbezogener Daten",
    26: "Datenverarbeitung fuer Zwecke des Beschaeftigungsverhaeltnisses",
    29: "Rechte der betroffenen Person und Aufsichtsbefugnis - Einschraenkungen der Art15-21-DSGVO-Rechte",
    32: "Informationspflicht bei Erhebung personenbezogener Daten bei der betroffenen Person - Ausnahmen",
    33: "Informationspflicht bei nicht bei der betroffenen Person erhobenen Daten - Ausnahmen",
    34: "Auskunftsrecht der betroffenen Person - Ausnahmen",
    35: "Recht auf Loeschung - Ausnahmen",
    38: "Betrieblicher Datenschutzbeauftragter - Bestellpflicht nicht-oeffentlicher Stellen",
    42: "Strafvorschriften",
    43: "Bussgeldvorschriften",
}

WS_RE = re.compile(r"\s+")


def clean(text: str) -> str:
    return WS_RE.sub(" ", text).strip()


def fetch(n: int) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / f"bdsg_{n}.html"
    if cache.exists():
        return cache.read_text(encoding="iso-8859-1")
    req = urllib.request.Request(
        BASE_URL.format(n=n), headers={"User-Agent": "Mozilla/5.0 (DSAR-Manager portfolio)"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
    text = raw.decode("iso-8859-1")
    cache.write_text(text, encoding="iso-8859-1")
    time.sleep(0.5)  # be polite to a public-sector server with no API
    return text


def parse_section(n: int, html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    header = soup.find("div", class_="jnheader")
    title_span = header.find("span", class_="jnentitel") if header else None
    title = clean(title_span.get_text(" ")) if title_span else ""

    body = soup.find("div", class_="jnhtml")
    paragraphs = []
    if body:
        for abs_div in body.find_all("div", class_="jurAbsatz"):
            text = clean(abs_div.get_text(" "))
            if not text:
                continue
            m = re.match(r"^\((\d+)\)\s*(.*)", text)
            number = int(m.group(1)) if m else None
            paragraphs.append({"number": number, "text": text})
    if not paragraphs and body:
        # Some short sections have no jurAbsatz wrapper at all.
        text = clean(body.get_text(" "))
        if text:
            paragraphs.append({"number": None, "text": text})

    return {
        "section": n,
        "title": title,
        "why_included": CURATED_SECTIONS[n],
        "paragraphs": paragraphs,
    }


def main() -> None:
    sections = []
    for n in sorted(CURATED_SECTIONS):
        html = fetch(n)
        entry = parse_section(n, html)
        if not entry["paragraphs"]:
            raise RuntimeError(f"§ {n} BDSG: keine Absaetze extrahiert, Parser pruefen")
        sections.append(entry)
        print(f"§ {n} BDSG: {entry['title']} ({len(entry['paragraphs'])} Absaetze)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "Bundesministerium der Justiz, gesetze-im-internet.de",
                "source_url_pattern": BASE_URL,
                "note": (
                    "Kuratierte Auswahl der fuer eine betriebliche Datenschutzbeauftragte "
                    "oder einen betrieblichen Datenschutzbeauftragten wiederkehrend relevanten "
                    "Vorschriften, nicht das vollstaendige BDSG."
                ),
                "sections": sections,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    total_paragraphs = sum(len(s["paragraphs"]) for s in sections)
    print(f"\n{len(sections)} Paragraphen ({total_paragraphs} Absaetze) geschrieben nach {OUT_PATH}")


if __name__ == "__main__":
    main()
