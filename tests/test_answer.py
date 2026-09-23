from rag_gdpr.answer import answer
from rag_gdpr.chunks import Chunk
from rag_gdpr.retriever import RetrievedChunk


def make_result(citation="Art. 15 Abs. 1 DSGVO", text="Beispieltext zur Auskunft."):
    chunk = Chunk(id="test-1", source="dsgvo", citation=citation, text=f"{citation}. {text}")
    return RetrievedChunk(chunk=chunk, score=0.9)


def test_answer_with_results_includes_citation():
    result = answer([make_result()])
    assert "Art. 15 Abs. 1 DSGVO" in result.text


def test_answer_without_results_says_so():
    result = answer([])
    assert result.sources == []
    assert "keine einschlaegige Fundstelle" in result.text
