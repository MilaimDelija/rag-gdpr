# RAG-GDPR

Retrieval mit Quellenangabe über die Datenschutz-Grundverordnung, eine kuratierte Auswahl des Bundesdatenschutzgesetzes und einen Index zentraler EDPB-Leitlinien.

## Zweck

Wer im Datenschutz arbeitet, stellt sich staendig dieselbe Frage in unterschiedlicher Formulierung: Was steht dazu genau im Gesetz, und in welchem Artikel oder Paragraphen? Dieses Werkzeug beantwortet Fragen ausschliesslich aus einem hinterlegten Korpus offizieller Rechtstexte und gibt zu jeder Antwort die exakte Fundstelle an, etwa Art. 15 Abs. 1 DSGVO oder § 38 Abs. 1 BDSG. Es erfindet nichts hinzu und sagt ausdruecklich, wenn eine Frage ausserhalb dessen liegt, was der Korpus abdeckt.

Das Werkzeug antwortet rein extraktiv: Es zeigt die einschlaegigen Textstellen selbst, nicht eine Umschreibung davon. Diese Entscheidung ist bewusst getroffen, nicht eine Einschraenkung aus Zeit- oder Kostengruenden. Ein Werkzeug, auf das man sich bei der korrekten Zitierung einer Vorschrift verlassen will, sollte keine fluessige Prosa erzeugen, die sich unbemerkt vom tatsaechlichen Wortlaut entfernt. Das hat einen weiteren Vorteil, der in einem datenschutzrechtlichen Kontext nicht nebensaechlich ist: Keine Anfrage und keine gefundene Textstelle verlaesst dabei jemals das System in Richtung eines externen Dienstes. Das Werkzeug laeuft vollstaendig offline.

## Inhalt des Korpus und seine Grenzen

Die Datenschutz-Grundverordnung ist vollstaendig enthalten: alle 99 Artikel und alle 173 Erwaegungsgruende, geladen aus der konsolidierten deutschen Fassung auf EUR-Lex (CELEX 32016R0679) und automatisiert in Artikel, Absaetze und, im Fall des Artikels 4, einzelne Begriffsbestimmungen zerlegt.

Das Bundesdatenschutzgesetz ist absichtlich nicht vollstaendig aufgenommen. Von seinen rund 85 Paragraphen betreffen viele das Verfahren der Aufsichtsbehoerden des Bundes oder Regelungen fuer oeffentliche Stellen, mit denen eine Datenschutzbeauftragte oder ein Datenschutzbeauftragter in einem privaten Unternehmen selten befasst ist. Aufgenommen ist eine kuratierte Auswahl von vierzehn Paragraphen, die im Alltag einer betrieblichen Datenschutzbeauftragten wiederkehren: Anwendungsbereich, Begriffsbestimmungen, Videoueberwachung, die Stellung der oder des Datenschutzbeauftragten samt Abberufungsschutz, besondere Kategorien personenbezogener Daten, Beschaeftigtendatenschutz, die gesetzlichen Einschraenkungen der Auskunfts- und Loeschungsrechte, die Bestellpflicht fuer den betrieblichen Datenschutzbeauftragten sowie die Straf- und Bussgeldvorschriften. Welche Erwaegung hinter der Aufnahme jedes einzelnen Paragraphen steht, ist im Feld `why_included` der Datei `rag_gdpr/corpus/processed/bdsg.json` dokumentiert.

Zu den EDPB-Leitlinien enthaelt das Werkzeug keinen Volltext, sondern einen Index von sieben zentralen Dokumenten mit amtlichem Titel, Fundstelle und einer kurzen, selbst formulierten Einordnung. Die Leitlinien selbst umfassen oft mehrere Dutzend Seiten; sie im Volltext einzubinden waere ein eigenes Projekt. Fuer die verbindliche Auslegung ist stets der unter jedem Eintrag verlinkte Volltext heranzuziehen.

## Funktionsweise

Jede Vorschrift wird bei der Ingestion in ihre kleinste zitierfaehige Einheit zerlegt, in aller Regel den einzelnen Absatz. Fuer die Anfrage wird daraus mit scikit-learn ein TF-IDF-Index gebildet und die Aehnlichkeit zur Suchanfrage per Kosinus-Distanz berechnet. Eine dedizierte Vektordatenbank waere fuer einen Korpus von einigen hundert Absaetzen unangemessen; TF-IDF mit Kosinus-Aehnlichkeit ist bei kurzen Rechtstexten mit trennscharfem Fachvokabular, etwa "Loeschung" oder "Einwilligung", ausserdem der Grund, warum ein dichtes Embedding-Modell hier keinen klaren Vorteil brachte.

Vier zusaetzliche Mechanismen wurden eingebaut, weil sie in der Praxis wiederholt zu falschen oder fehlenden Treffern gefuehrt haben. Erstens werden deutsche Umlaute vor der Indexierung und bei jeder Anfrage auf eine gemeinsame Schreibweise normalisiert, weil ein Umlaut ebenso haeufig als "ue", "oe" oder "ae" eingegeben wird wie in seiner eigentlichen Form, und ein reiner TF-IDF-Abgleich beide sonst als voellig verschiedene Woerter behandelt. Zweitens wird ein Bindestrich, der zwei Wortteile ohne Leerzeichen verbindet, vor der Tokenisierung entfernt, weil der Gesetzestext ein zusammengesetztes Substantiv wie "Datenschutz-Folgenabschätzung" hyphenisiert, waehrend dieselbe Frage haeufig als ein einziges Wort formuliert wird; ein Bindestrich mit Leerzeichen davor und danach bleibt unveraendert. Drittens wird jedes Wort mit dem Snowball-Stemmer fuer Deutsch auf seinen Wortstamm reduziert, weil eine Frage "Datenschutzbeauftragter" schreibt, waehrend der Gesetzestext "Datenschutzbeauftragte" oder "Datenschutzbeauftragten" verwendet, und diese Formen ohne Stemming als unterschiedliche Begriffe gezaehlt wuerden. Viertens werden gaengige umgangssprachliche Begriffe aus der Praxis, etwa "Datenpanne", "Kamera" oder "bestellen" statt "benennen", bei der Anfrage um die entsprechenden Gesetzesbegriffe ergaenzt, ohne den indexierten Originaltext zu veraendern, da sonst eine Anfrage nach einer "Datenpanne" die einschlaegigen Art. 33 und 34 DSGVO verfehlen wuerde, weil das Gesetz konsequent von einer "Verletzung des Schutzes personenbezogener Daten" spricht. Fuer Definitionsfragen wie "Was ist ein Auftragsverarbeiter?" wird zusaetzlich direkt in den 26 Begriffsbestimmungen aus Art. 4 DSGVO nachgeschlagen, da ein haeufig im gesamten Gesetzestext vorkommender Begriff sonst durch TF-IDF ein zu geringes Gewicht erhaelt, um zuverlaessig an erster Stelle zu erscheinen.

## Installation und Nutzung

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m rag_gdpr.retriever      # baut den Suchindex aus dem mitgelieferten Korpus
python3 -m rag_gdpr.app            # startet die Weboberflaeche unter http://127.0.0.1:5001
```

Ohne vorherigen Aufruf von `rag_gdpr.retriever` baut sowohl die Weboberflaeche als auch die Kommandozeile den Index beim ersten Aufruf automatisch auf; das dauert wenige Sekunden.

Kommandozeile:

```bash
python3 -m rag_gdpr.cli ask "Innerhalb welcher Frist muss ein Auskunftsersuchen beantwortet werden?"
python3 -m rag_gdpr.cli ask "Wann muss ein Datenschutzbeauftragter bestellt werden?" --k 3
python3 -m rag_gdpr.cli ask "Was ist eine Einwilligung?" --source dsgvo
```

## Den Korpus neu aufbauen

Die verarbeiteten JSON-Dateien unter `rag_gdpr/corpus/processed/` sind Teil des Repositories und muessen fuer die Nutzung nicht neu erzeugt werden. Wer den DSGVO- oder BDSG-Text bei einer kuenftigen Konsolidierung erneut von der Quelle laden moechte:

```bash
python3 -m rag_gdpr.corpus.build_gdpr    # laedt und parst EUR-Lex neu
python3 -m rag_gdpr.corpus.build_bdsg    # laedt die kuratierten Paragraphen neu
python3 -m rag_gdpr.retriever            # baut den Index aus den aktualisierten Daten neu
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Die Testsuite prueft unter anderem, dass alle 99 Artikel und alle 173 Erwaegungsgruende geladen werden, dass die 26 Begriffsbestimmungen aus Art. 4 einzeln zitierfaehig sind, dass eine umlauttransliterierte und eine native Schreibweise dieselben Treffer liefern, dass eine umgangssprachliche Anfrage zu einer Datenpanne tatsaechlich Art. 33 und 34 DSGVO findet, und dass der Definitions-Direktzugriff einen haeufig vorkommenden Begriff wie "Auftragsverarbeiter" korrekt an die erste Stelle setzt.

## Grenzen

TF-IDF ist ein Verfahren auf Wortebene; eine Anfrage, die ein Thema ausschliesslich mit Synonymen umschreibt, die weder im Gesetzestext noch in der kuratierten Synonymliste vorkommen, kann trotz thematischer Naehe eine schwache oder falsche Fundstelle liefern. Innerhalb eines mehrere Absaetze umfassenden Artikels kann ausserdem der Absatz mit den meisten Wiederholungen der gesuchten Begriffe vor dem inhaltlich treffenderen Absatz erscheinen, etwa wenn Art. 35 Abs. 2 DSGVO den Begriff "Datenschutz-Folgenabschätzung" ein zweites Mal aufgreift, waehrend der einschlaegigere Art. 35 Abs. 1 ihn nur einmal im Titel traegt; ein Blick auf die Nachbarabsaetze der obersten Treffer bleibt daher sinnvoll. Die kuratierte BDSG-Auswahl und der EDPB-Index sind, wie oben beschrieben, bewusst unvollstaendig. Das Werkzeug ersetzt keine Rechtsberatung im Einzelfall und keine Lektuere des vollstaendigen Gesetzestextes bei einer Entscheidung mit rechtlicher Tragweite.
