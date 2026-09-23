import pytest

from rag_gdpr.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_index_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "DSGVO".encode("utf-8") in resp.data


def test_search_returns_result(client):
    resp = client.post("/", data={"query": "Was ist ein Auftragsverarbeiter?"})
    assert resp.status_code == 200
    assert "Art. 4 Nr. 8 DSGVO".encode("utf-8") in resp.data


def test_search_with_source_filter(client):
    resp = client.post("/", data={"query": "Datenschutzbeauftragte", "source": "bdsg"})
    assert resp.status_code == 200


def test_empty_query_shows_no_result(client):
    resp = client.post("/", data={"query": ""})
    assert resp.status_code == 200
