"""Loads the three processed corpora (GDPR, BDSG, EDPB index) into a single,
uniformly structured list of citable chunks.

A chunk is the retrieval unit: for GDPR and BDSG this is one paragraph (or,
where a norm carries no explicit paragraph numbering, the whole article or
section), and for the EDPB index it is one guideline's summary entry. Every
chunk carries a precise citation string, so that whatever a retrieval or an
answer returns can be traced back to an exact provision rather than a vague
"according to the GDPR".
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent / "corpus" / "processed"


@dataclass
class Chunk:
    id: str
    source: str  # "dsgvo" | "bdsg" | "edpb"
    citation: str
    text: str
    url: str = ""


def load_gdpr_chunks() -> list[Chunk]:
    path = PROCESSED_DIR / "gdpr.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    chunks: list[Chunk] = []
    for art in data["articles"]:
        n = art["article"]
        title = art["title"]
        for para in art["paragraphs"]:
            point = para.get("point")
            if para["number"] is not None:
                citation = f"Art. {n} Abs. {para['number']} DSGVO"
                cid = f"dsgvo-art{n}-{para['number']}"
            elif point is not None:
                citation = f"Art. {n} Nr. {point} DSGVO"
                cid = f"dsgvo-art{n}-nr{point}"
            else:
                citation = f"Art. {n} DSGVO"
                cid = f"dsgvo-art{n}"
            text = f"Art. {n} DSGVO ({title}). {para['text']}"
            chunks.append(Chunk(id=cid, source="dsgvo", citation=citation, text=text,
                                 url=data.get("source_url", "")))
    for rec in data["recitals"]:
        n = rec["recital"]
        citation = f"Erwägungsgrund {n} DSGVO"
        cid = f"dsgvo-erwg{n}"
        text = f"Erwägungsgrund {n} DSGVO. {rec['text']}"
        chunks.append(Chunk(id=cid, source="dsgvo", citation=citation, text=text,
                             url=data.get("source_url", "")))
    return chunks


def load_bdsg_chunks() -> list[Chunk]:
    path = PROCESSED_DIR / "bdsg.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    chunks: list[Chunk] = []
    for sec in data["sections"]:
        n = sec["section"]
        title = sec["title"]
        for para in sec["paragraphs"]:
            if para["number"] is not None:
                citation = f"§ {n} Abs. {para['number']} BDSG"
                cid = f"bdsg-par{n}-{para['number']}"
            else:
                citation = f"§ {n} BDSG"
                cid = f"bdsg-par{n}"
            text = f"§ {n} BDSG ({title}). {para['text']}"
            chunks.append(Chunk(id=cid, source="bdsg", citation=citation, text=text))
    return chunks


def load_edpb_chunks() -> list[Chunk]:
    path = PROCESSED_DIR / "edpb_index.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    chunks: list[Chunk] = []
    for g in data["guidelines"]:
        citation = f"{g['body']}, {g['title']}"
        text = f"{g['title']}. Thema: {g['topic']}. {g['summary']}"
        chunks.append(Chunk(id=g["id"], source="edpb", citation=citation, text=text, url=g["url"]))
    return chunks


def load_all_chunks() -> list[Chunk]:
    return load_gdpr_chunks() + load_bdsg_chunks() + load_edpb_chunks()
