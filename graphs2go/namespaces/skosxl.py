from graphs2go.models import rdf


class SKOSXL:
    _BASE_IRI = "http://www.w3.org/2008/05/skos-xl#"

    # Classes
    Label = rdf.Iri(_BASE_IRI + "Label")

    # Properties
    altLabel = rdf.Iri(_BASE_IRI + "altLabel")
    hiddenLabel = rdf.Iri(_BASE_IRI + "hiddenLabel")
    labelRelation = rdf.Iri(_BASE_IRI + "labelRelation")
    literalForm = rdf.Iri(_BASE_IRI + "literalForm")
    prefLabel = rdf.Iri(_BASE_IRI + "prefLabel")
