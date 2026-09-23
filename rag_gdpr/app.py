"""Flask front end for the legal retrieval tool.

Run with `python -m rag_gdpr.app`.
"""

from __future__ import annotations

import os

from flask import Flask, render_template, request

from .answer import answer
from .retriever import INDEX_PATH, Retriever, build_index

_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        if not INDEX_PATH.exists():
            build_index()
        _retriever = Retriever()
    return _retriever


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        query = ""
        result = None
        source_filter = None
        if request.method == "POST":
            query = request.form.get("query", "").strip()
            source_filter = request.form.get("source") or None
            if query:
                retriever = get_retriever()
                results = retriever.search(query, k=5, source=source_filter)
                result = answer(results)
        return render_template(
            "index.html",
            query=query,
            result=result,
            source_filter=source_filter,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
