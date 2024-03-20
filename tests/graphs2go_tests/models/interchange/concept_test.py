from rdflib import URIRef

from graphs2go.models import interchange


def test_builder(interchange_node: interchange.Concept) -> None:  # noqa: ARG001
    pass


def test_rdf_type_uri() -> None:
    assert isinstance(interchange.Concept.rdf_type_uri(), URIRef)
