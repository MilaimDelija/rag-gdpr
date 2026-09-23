"""A compact German stop-word list for TF-IDF retrieval.

Scikit-learn ships no German list, and pulling one from an NLTK corpus
download would add an external dependency, at runtime, for a handful of
function words. This list covers articles, pronouns, conjunctions,
prepositions and common auxiliary verb forms, which is what actually
inflates term-frequency noise in German legal text; it does not aim at
linguistic completeness.
"""

from .analyzer_de import stem
from .text_normalize import normalize_de

_RAW_STOPWORDS = """
    aber alle allem allen aller alles als also am an ander andere anderem
    anderen anderer anderes anderm andern anderr anders auch auf aus bei bin
    bis bist da damit dann der den des dem die das dass daß derselbe
    derselben denselben desselben demselben dieselbe dieselben dasselbe dazu
    dein deine dass du durch ein eine einem einen einer eines einig einige
    einigem einigen einiger einiges einmal er ihn ihm es etwas euer eure
    für gegen gewesen hab habe haben hat hatte hatten hier hin hinter ich
    mich mir ihr ihre ihrem ihren ihrer ihres euch im in indem ins ist jede
    jedem jeden jeder jedes jene jenem jenen jener jenes jetzt kann kein
    keine keinem keinen keiner keines können könnte machen man manche
    manchem manchen mancher manches mein meine meinem meinen meiner meines
    mit muss musste nach nicht nichts noch nun nur ob oder ohne sehr sein
    seine seinem seinen seiner seines selbst sich sie ihnen sind so solche
    solchem solchen solcher solches soll sollte sondern sonst über um und
    uns unse unser unter viel vom von vor während war waren warst was weil
    weiter weitere wenn werde werden wie wieder will wir wird wirst wo
    wollen wollte würde würden zu zum zur zwar zwischen sowie oder bzw
    gemäß gemaess soweit sofern jedoch dabei dadurch dafür damit ferner
    hierbei hierzu hiervon insbesondere sowohl sonstige jeweiligen jeweils
    """.split()

# Pre-normalised (ue/oe/ae/ss instead of ü/ö/ä/ß) and pre-stemmed, because
# GermanAnalyzer normalises and stems every corpus and query token before
# comparing it against this set.
GERMAN_STOPWORDS = frozenset(normalize_de(w) for w in _RAW_STOPWORDS)
GERMAN_STOPWORDS_STEMMED = frozenset(stem(w) for w in GERMAN_STOPWORDS)
