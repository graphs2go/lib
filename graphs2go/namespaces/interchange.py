from graphs2go.models import rdf


class INTERCHANGE:
    _BASE_IRI = "http://www.graphs2go.com/schema/interchange#"

    # Classes
    Label = rdf.Iri(_BASE_IRI + "Label")
    Node = rdf.Iri(_BASE_IRI + "Node")
    Property = rdf.Iri(_BASE_IRI + "Property")
    Relationship = rdf.Iri(_BASE_IRI + "Relationship")

    # Properties
    label = rdf.Iri(_BASE_IRI + "label")  # Node->Label
    nodeType = rdf.Iri(_BASE_IRI + "nodeType")
    property = rdf.Iri(_BASE_IRI + "property")  # Node -> Property
    relationship = rdf.Iri(_BASE_IRI + "relationship")  # Node -> Relationship
