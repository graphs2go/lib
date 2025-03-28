from rdflib import DCTERMS, RDF, RDFS, SKOS, XSD

from graphs2go.models import rdf

from .dash import DASH as DASH
from .interchange import INTERCHANGE as INTERCHANGE
from .sdo import SDO as SDO
from .skosxl import SKOSXL as SKOSXL

NAMESPACE_PREFIXES: rdf.NamespacePrefixes = {
    DASH.PREFIX: DASH.BASE_IRI,
    "dct": rdf.Iri(DCTERMS._NS),
    INTERCHANGE.PREFIX: INTERCHANGE.BASE_IRI,
    "rdf": rdf.Iri(RDF._NS),
    "rdfs": rdf.Iri(RDFS._NS),
    SDO.PREFIX: SDO.BASE_IRI,
    "skos": rdf.Iri(SKOS._NS),
    SKOSXL.PREFIX: SKOSXL.BASE_IRI,
    "xsd": rdf.Iri(XSD._NS),
}
