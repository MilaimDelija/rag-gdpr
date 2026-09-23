from rag_gdpr.text_normalize import normalize_de


def test_umlauts_normalised_to_ascii():
    assert normalize_de("Überwachung") == "ueberwachung"
    assert normalize_de("Loeschung") == "loeschung"
    assert normalize_de("Löschung") == "loeschung"


def test_eszett_normalised():
    assert normalize_de("Straße") == "strasse"


def test_case_insensitive():
    assert normalize_de("DATENSCHUTZ") == "datenschutz"


def test_matches_transliterated_and_native_form():
    assert normalize_de("Videoüberwachung") == normalize_de("Videoueberwachung")


def test_compound_hyphen_is_joined():
    assert normalize_de("Datenschutz-Folgenabschätzung") == normalize_de("Datenschutzfolgenabschätzung")


def test_spaced_dash_is_not_joined():
    # A dash used as punctuation, with surrounding whitespace, is not a
    # compound joiner and must not merge the two words either side of it.
    assert normalize_de("Verantwortliche - oder") == "verantwortliche - oder"
