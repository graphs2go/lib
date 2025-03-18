from graphs2go.models import rdf


class DASH:
    BASE_IRI = rdf.Iri("http://datashapes.org/dash#")
    PREFIX = "dash"

    # Properties
    abstract = rdf.Iri(BASE_IRI + "abstract")
    reifiableBy = rdf.Iri(BASE_IRI + "reifiableBy")
    viewer = rdf.Iri(BASE_IRI + "viewer")

    # Resources
    DetailsViewer = rdf.Iri(BASE_IRI + "DetailsViewer")
