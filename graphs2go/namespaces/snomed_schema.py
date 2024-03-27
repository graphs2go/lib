from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class SNOMED_SCHEMA(DefinedNamespace):  # noqa: N801
    _NS = Namespace("http://snomed-ct.graphs2go.org/schema/")

    _fail = False
    _warn = False

    normativeReference: URIRef  # URI link to authoritative source
