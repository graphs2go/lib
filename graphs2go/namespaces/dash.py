from graphs2go.models import rdf


class DASH:
    _BASE_IRI = "http://datashapes.org/dash#"

    # Properties
    abstract = rdf.Iri(_BASE_IRI + "abstract")
    reifiableBy = rdf.Iri(_BASE_IRI + "reifiableBy")
    viewer = rdf.Iri(_BASE_IRI + "viewer")

    # Resources
    DetailsViewer = rdf.Iri(_BASE_IRI + "DetailsViewer")
