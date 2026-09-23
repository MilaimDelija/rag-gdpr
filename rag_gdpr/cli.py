"""Command-line interface for querying the legal corpus.

Examples:
    python -m rag_gdpr.cli ask "Innerhalb welcher Frist muss ein Auskunftsersuchen beantwortet werden?"
    python -m rag_gdpr.cli ask "Wann muss ein Datenschutzbeauftragter bestellt werden?" --k 3
    python -m rag_gdpr.cli reindex
"""

from __future__ import annotations

import argparse
import sys

from .answer import answer
from .retriever import INDEX_PATH, Retriever, build_index


def cmd_ask(args: argparse.Namespace) -> int:
    if not INDEX_PATH.exists():
        print("Kein Index gefunden, baue ihn jetzt auf ...", file=sys.stderr)
        build_index()
    retriever = Retriever()
    results = retriever.search(args.query, k=args.k, source=args.source)
    result = answer(results)
    print(result.text)
    return 0


def cmd_reindex(args: argparse.Namespace) -> int:
    build_index()
    print(f"Index neu aufgebaut unter {INDEX_PATH}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag_gdpr", description="RAG ueber DSGVO, BDSG und EDPB-Leitlinien")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ask = sub.add_parser("ask", help="Eine Frage stellen")
    p_ask.add_argument("query")
    p_ask.add_argument("--k", type=int, default=5, help="Anzahl der Fundstellen")
    p_ask.add_argument("--source", choices=["dsgvo", "bdsg", "edpb"], default=None)
    p_ask.set_defaults(func=cmd_ask)

    p_reindex = sub.add_parser("reindex", help="TF-IDF-Index neu aufbauen")
    p_reindex.set_defaults(func=cmd_reindex)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
