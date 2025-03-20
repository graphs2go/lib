from rdflib import DCTERMS, RDF, RDFS, SKOS  # noqa: F401
from .dash import DASH as DASH
from .interchange import INTERCHANGE as INTERCHANGE
from .sdo import SDO as SDO
from .skosxl import SKOSXL as SKOSXL
from graphs2go.models import rdf

PREFIXES: dict[str, rdf.Iri] = {
    DASH.PREFIX: DASH.BASE_IRI,
    "dct": rdf.Iri(DCTERMS._NS),
    INTERCHANGE.PREFIX: INTERCHANGE.BASE_IRI,
    "rdf": rdf.Iri(RDF._NS),
    "rdfs": rdf.Iri(RDFS._NS),
    SDO.PREFIX: SDO.BASE_IRI,
    "skos": rdf.Iri(SKOS._NS),
    SKOSXL.PREFIX: SKOSXL.BASE_IRI,
}
