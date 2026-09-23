"""Parses the official consolidated German GDPR text from EUR-Lex (CELEX 32016R0679)
into structured JSON, one entry per article paragraph and one per recital.

The EUR-Lex HTML for this act uses a stable, machine-readable structure introduced
with the ELI (European Legislation Identifier) markup: each article sits in a
<div class="eli-subdivision" id="art_N">, and within it every numbered paragraph
sits in its own <div id="NNN.MMM">. Lettered sub-points of a paragraph are nested
two-column tables inside that same paragraph div, so taking the paragraph div's
full text already yields the complete paragraph including its sub-points. Articles
without explicit paragraph numbering, such as Article 4 (definitions), instead
carry their numbered list directly as sibling tables, which are collected into a
single unnumbered chunk for that article.

Run as: python3 -m rag_gdpr.corpus.build_gdpr
Reads:  rag_gdpr/corpus/raw/gdpr_eurlex.html   (saved via curl from EUR-Lex)
Writes: rag_gdpr/corpus/processed/gdpr.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

RAW_PATH = Path(__file__).parent / "raw" / "gdpr_eurlex.html"
OUT_PATH = Path(__file__).parent / "processed" / "gdpr.json"

WS_RE = re.compile(r"\s+")


def clean(text: str) -> str:
    return WS_RE.sub(" ", text).strip()


def extract_article(div) -> dict:
    art_id = div["id"]  # e.g. "art_6"
    number = int(art_id.split("_", 1)[1])

    title_p = div.find("p", class_="oj-ti-art")
    title_div = div.find("div", class_="eli-title")
    subtitle = clean(title_div.get_text(" ")) if title_div else ""

    paragraphs = []
    loose_intro = []
    loose_points = []  # (point_number, text) for top-level numbered list items

    for child in div.find_all(recursive=False):
        if child is title_p or child is title_div:
            continue
        cid = child.get("id", "") if child.name == "div" else ""
        if child.name == "div" and re.match(r"^\d+\.\d+$", cid):
            text = clean(child.get_text(" "))
            m = re.match(r"^\((\d+)\)\s*(.*)", text)
            if m:
                paragraphs.append({"number": int(m.group(1)), "point": None, "text": text})
            else:
                paragraphs.append({"number": None, "point": None, "text": text})
        elif child.name == "table":
            tds = child.find_all("td")
            if len(tds) >= 2:
                label = clean(tds[0].get_text(" "))
                content = clean(tds[1].get_text(" "))
                m = re.match(r"^(\d+)\.$", label)
                if m:
                    loose_points.append((int(m.group(1)), f"{label} {content}"))
                else:
                    loose_intro.append(f"{label} {content}")
            else:
                loose_intro.append(clean(child.get_text(" ")))
        else:
            text = clean(child.get_text(" "))
            if text:
                loose_intro.append(text)

    if loose_points and not paragraphs:
        # Articles such as Art. 4 (definitions) carry a top-level numbered
        # list with no enclosing paragraph numbering. Each numbered point
        # becomes its own citable chunk ("Art. 4 Nr. 7 DSGVO") instead of
        # being merged into one oversized, hard-to-retrieve blob; the
        # introductory sentence is kept as a short unnumbered lead-in.
        for text in loose_intro:
            paragraphs.append({"number": None, "point": None, "text": text})
        for point_number, text in sorted(loose_points):
            paragraphs.append({"number": None, "point": point_number, "text": text})
    elif loose_intro and not paragraphs:
        paragraphs.append({"number": None, "point": None, "text": " ".join(loose_intro)})
    elif loose_intro:
        # Rare mixed case: leading or trailing unwrapped text alongside
        # numbered paragraphs. Keep it as an unnumbered leading chunk so
        # nothing from the official text is silently dropped.
        paragraphs.insert(0, {"number": None, "point": None, "text": " ".join(loose_intro)})

    return {
        "article": number,
        "title": subtitle,
        "paragraphs": paragraphs,
    }


def extract_recital(div) -> dict:
    rct_id = div["id"]  # e.g. "rct_1"
    number = int(rct_id.split("_", 1)[1])
    text = clean(div.get_text(" "))
    text = re.sub(r"^\(\d+\)\s*", "", text)
    return {"recital": number, "text": text}


def main() -> None:
    with open(RAW_PATH, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    container = soup.find("div", class_="eli-container")
    if container is None:
        raise RuntimeError(
            "Konnte den Dokumentcontainer nicht finden; hat sich das EUR-Lex-Layout geaendert?"
        )

    articles = []
    for div in container.find_all("div", id=re.compile(r"^art_\d+$")):
        articles.append(extract_article(div))
    articles.sort(key=lambda a: a["article"])

    recitals = []
    for div in container.find_all("div", id=re.compile(r"^rct_\d+$")):
        recitals.append(extract_recital(div))
    recitals.sort(key=lambda r: r["recital"])

    if len(articles) != 99:
        raise RuntimeError(f"Erwartet 99 Artikel, gefunden {len(articles)}")
    if len(recitals) != 173:
        raise RuntimeError(f"Erwartet 173 Erwaegungsgruende, gefunden {len(recitals)}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "source": "EUR-Lex, konsolidierte deutsche Fassung, CELEX 32016R0679",
                "source_url": "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32016R0679",
                "articles": articles,
                "recitals": recitals,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    total_paragraphs = sum(len(a["paragraphs"]) for a in articles)
    print(f"{len(articles)} Artikel ({total_paragraphs} Absaetze), {len(recitals)} Erwaegungsgruende geschrieben nach {OUT_PATH}")


if __name__ == "__main__":
    main()
