from rdflib import DCTERMS, RDF, RDFS, SKOS, XSD

from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.namespace_prefixes import NamespacePrefixes

from .dash import DASH as DASH
from .interchange import INTERCHANGE as INTERCHANGE
from .sdo import SDO as SDO
from .skosxl import SKOSXL as SKOSXL

NAMESPACE_PREFIXES: NamespacePrefixes = {
    DASH.PREFIX: DASH.BASE_IRI,
    "dct": Iri(DCTERMS._NS),
    INTERCHANGE.PREFIX: INTERCHANGE.BASE_IRI,
    "rdf": Iri(RDF._NS),
    "rdfs": Iri(RDFS._NS),
    SDO.PREFIX: SDO.BASE_IRI,
    "skos": Iri(SKOS._NS),
    SKOSXL.PREFIX: SKOSXL.BASE_IRI,
    "xsd": Iri(XSD._NS),
}
