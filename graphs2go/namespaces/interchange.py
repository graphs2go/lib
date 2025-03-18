from rdflib.namespace import DefinedNamespace, Namespace
from graphs2go.models import rdf


class INTERCHANGE(DefinedNamespace):
    _NS = Namespace("http://www.graphs2go.com/schema/interchange#")

    _fail = True

    # Classes
    Label: rdf.Iri
    Node: rdf.Iri
    Property: rdf.Iri
    Relationship: rdf.Iri

    # Properties
    label: rdf.Iri  # Node->Label
    nodeType: rdf.Iri
    property: rdf.Iri  # Node -> Property
    relationship: rdf.Iri  # Node -> Relationship
