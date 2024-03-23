from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class SKOSXL(DefinedNamespace):
    _NS = Namespace("http://www.w3.org/2008/05/skos-xl#")

    _fail = True

    # Classes
    Label: URIRef

    # Properties
    altLabel: URIRef
    hiddenLabel: URIRef
    labelRelation: URIRef
    literalForm: URIRef
    prefLabel: URIRef
