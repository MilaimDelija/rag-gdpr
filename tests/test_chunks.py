from rag_gdpr.chunks import load_all_chunks, load_bdsg_chunks, load_edpb_chunks, load_gdpr_chunks


def test_gdpr_chunks_load_and_cover_all_99_articles():
    chunks = load_gdpr_chunks()
    article_numbers = {
        int(c.citation.split(" ")[1]) for c in chunks if c.citation.startswith("Art. ")
    }
    assert article_numbers == set(range(1, 100))


def test_gdpr_includes_recitals():
    chunks = load_gdpr_chunks()
    recital_citations = [c for c in chunks if c.citation.startswith("Erwägungsgrund")]
    assert len(recital_citations) == 173


def test_article_4_definitions_are_split_into_individual_points():
    chunks = load_gdpr_chunks()
    art4_points = [c for c in chunks if c.citation.startswith("Art. 4 Nr.")]
    # The GDPR defines 26 terms in Art. 4.
    assert len(art4_points) == 26
    citations = {c.citation for c in art4_points}
    assert "Art. 4 Nr. 1 DSGVO" in citations
    assert "Art. 4 Nr. 8 DSGVO" in citations


def test_article_4_point_8_is_auftragsverarbeiter():
    chunks = load_gdpr_chunks()
    by_citation = {c.citation: c for c in chunks}
    assert "Auftragsverarbeiter" in by_citation["Art. 4 Nr. 8 DSGVO"].text


def test_article_6_paragraph_1_contains_all_lettered_points():
    chunks = load_gdpr_chunks()
    by_citation = {c.citation: c for c in chunks}
    text = by_citation["Art. 6 Abs. 1 DSGVO"].text
    for letter_marker in ("a)", "b)", "c)", "d)", "e)", "f)"):
        assert letter_marker in text


def test_bdsg_chunks_load_and_are_curated_subset():
    chunks = load_bdsg_chunks()
    assert len(chunks) > 0
    section_numbers = {int(c.citation.split(" ")[1].rstrip(".")) for c in chunks}
    assert 38 in section_numbers  # betrieblicher Datenschutzbeauftragter
    assert 26 in section_numbers  # Beschaeftigtendatenverarbeitung


def test_edpb_chunks_have_urls():
    chunks = load_edpb_chunks()
    assert len(chunks) > 0
    assert all(c.url.startswith("http") for c in chunks)


def test_load_all_combines_every_source():
    all_chunks = load_all_chunks()
    sources = {c.source for c in all_chunks}
    assert sources == {"dsgvo", "bdsg", "edpb"}


def test_all_chunk_ids_are_unique():
    all_chunks = load_all_chunks()
    ids = [c.id for c in all_chunks]
    assert len(ids) == len(set(ids))
