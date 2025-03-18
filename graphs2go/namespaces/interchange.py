from graphs2go.models import rdf


class INTERCHANGE:
    BASE_IRI = rdf.Iri("http://www.graphs2go.com/schema/interchange#")
    PREFIX = "interchange"

    # Classes
    Label = rdf.Iri(BASE_IRI + "Label")
    Node = rdf.Iri(BASE_IRI + "Node")
    Property = rdf.Iri(BASE_IRI + "Property")
    Relationship = rdf.Iri(BASE_IRI + "Relationship")

    # Properties
    label = rdf.Iri(BASE_IRI + "label")  # Node->Label
    nodeType = rdf.Iri(BASE_IRI + "nodeType")
    property = rdf.Iri(BASE_IRI + "property")  # Node -> Property
    relationship = rdf.Iri(BASE_IRI + "relationship")  # Node -> Relationship
