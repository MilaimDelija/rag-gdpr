from rag_gdpr.cli import main


def test_cli_ask_prints_extractive_answer(capsys):
    rc = main(["ask", "Was ist ein Auftragsverarbeiter?", "--k", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Art. 4 Nr. 8 DSGVO" in out


def test_cli_ask_respects_source_filter(capsys):
    rc = main(["ask", "Datenschutzbeauftragte Benennung", "--k", "3", "--source", "bdsg"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DSGVO" not in out.replace("Datenschutzbeauftragte", "")


def test_cli_reindex(capsys):
    rc = main(["reindex"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Index neu aufgebaut" in out
