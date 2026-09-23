"""Turns a set of retrieved chunks into an answer.

The tool answers purely extractively: it returns the retrieved provisions
verbatim, each with its citation, and states plainly when nothing relevant
was found. This is a deliberate choice, not a shortcut. A tool that a data
protection officer relies on for citing the correct article should never
produce fluent prose that quietly drifts from what the source text actually
says; showing the provisions themselves is the safer default and is often
more useful in practice than a paraphrase. It also means no query and no
retrieved passage ever leaves the system to a third-party service, which
matters for a tool used in a data-protection context.
"""

from __future__ import annotations

from dataclasses import dataclass

from .retriever import RetrievedChunk


@dataclass
class Answer:
    text: str
    sources: list[RetrievedChunk]


def answer(results: list[RetrievedChunk]) -> Answer:
    if not results:
        return Answer(
            text=(
                "Zu dieser Frage enthaelt der hinterlegte Korpus keine einschlaegige Fundstelle. "
                "Das kann daran liegen, dass die Frage ausserhalb der DSGVO, der kuratierten "
                "BDSG-Auswahl und des EDPB-Leitlinienindex liegt, oder an der Formulierung der Suche."
            ),
            sources=[],
        )
    lines = ["Folgende Fundstellen sind zu dieser Frage einschlaegig:\n"]
    for r in results:
        lines.append(f"{r.chunk.citation}\n{r.chunk.text.split('. ', 1)[-1] if '. ' in r.chunk.text else r.chunk.text}\n")
    return Answer(text="\n".join(lines), sources=results)
