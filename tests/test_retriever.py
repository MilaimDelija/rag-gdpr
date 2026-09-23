import pytest

from rag_gdpr.retriever import Retriever, build_index


@pytest.fixture(scope="module")
def retriever(tmp_path_factory):
    index_path = tmp_path_factory.mktemp("index") / "index.pkl"
    build_index(index_path=index_path)
    return Retriever(index_path)


def test_search_returns_ranked_results(retriever):
    results = retriever.search("Auskunftsrecht der betroffenen Person", k=3)
    assert len(results) == 3
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_empty_query_returns_nothing(retriever):
    assert retriever.search("") == []
    assert retriever.search("   ") == []


def test_source_filter_restricts_results(retriever):
    results = retriever.search("Datenschutzbeauftragte Benennung", k=5, source="bdsg")
    assert all(r.chunk.source == "bdsg" for r in results)


def test_umlaut_transliteration_matches_native_spelling(retriever):
    native = retriever.search("Videoüberwachung Kunden", k=3)
    transliterated = retriever.search("Videoueberwachung Kunden", k=3)
    native_ids = {r.chunk.id for r in native}
    translit_ids = {r.chunk.id for r in transliterated}
    assert native_ids == translit_ids


def test_hyphenated_compound_matches_unhyphenated_query(retriever):
    results = retriever.search("Muss ich eine Datenschutzfolgenabschaetzung durchfuehren?", k=5)
    citations = {r.chunk.citation for r in results}
    assert any(c.startswith("Art. 35") for c in citations)


def test_colloquial_datenpanne_finds_breach_articles(retriever):
    results = retriever.search("Was tun bei einer Datenpanne?", k=5)
    citations = {r.chunk.citation for r in results}
    assert any(c.startswith("Art. 33") or c.startswith("Art. 34") for c in citations)


def test_definition_lookup_shortcut_for_common_term(retriever):
    results = retriever.search("Was ist ein Auftragsverarbeiter?", k=3)
    assert results[0].chunk.citation == "Art. 4 Nr. 8 DSGVO"
    assert results[0].score == 1.0


def test_definition_lookup_ignores_unknown_term(retriever):
    # Falls through to ordinary TF-IDF search rather than crashing.
    results = retriever.search("Was ist eine Kaffeemaschine?", k=3)
    assert isinstance(results, list)
