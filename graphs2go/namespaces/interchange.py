from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class INTERCHANGE(DefinedNamespace):
    _NS = Namespace("http://www.graphs2go.com/schema/interchange#")

    _fail = True

    # Classes
    Label: URIRef
    Node: URIRef
    Property: URIRef
    Relationship: URIRef
    RelationshipGroup: URIRef
