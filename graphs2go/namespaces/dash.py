from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class DASH(DefinedNamespace):
    _NS = Namespace("http://datashapes.org/dash#")

    _fail = True

    # Properties

    abstract: URIRef
    reifiableBy: URIRef
    viewer: URIRef

    # Resources
    DetailsViewer: URIRef
