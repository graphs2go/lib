from graphs2go.models import rdf
from graphs2go.namespaces import (
    DASH,
    DCTERMS,
    RDF,
    RDFS,
    SDO,
    SKOS,
    SKOSXL,
    INTERCHANGE,
)

PREFIXES: dict[str, rdf.Iri] = {
    DASH.PREFIX: DASH.BASE_IRI,
    "dct": rdf.Iri(DCTERMS[""]),
    INTERCHANGE.PREFIX: INTERCHANGE.BASE_IRI,
    "rdf": rdf.Iri(RDF[""]),
    "rdfs": rdf.Iri(RDFS[""]),
    SDO.PREFIX: SDO.BASE_IRI,
    "skos": rdf.Iri(SKOS[""]),
    SKOSXL.PREFIX: SKOSXL.BASE_IRI,
}
