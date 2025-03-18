from graphs2go.models import rdf


class SKOSXL:
    BASE_IRI = rdf.Iri("http://www.w3.org/2008/05/skos-xl#")
    PREFIX = "skosxl"

    # Classes
    Label = rdf.Iri(BASE_IRI + "Label")

    # Properties
    altLabel = rdf.Iri(BASE_IRI + "altLabel")
    hiddenLabel = rdf.Iri(BASE_IRI + "hiddenLabel")
    labelRelation = rdf.Iri(BASE_IRI + "labelRelation")
    literalForm = rdf.Iri(BASE_IRI + "literalForm")
    prefLabel = rdf.Iri(BASE_IRI + "prefLabel")
