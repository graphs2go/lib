from rdflib import URIRef

from graphs2go.models import interchange


def test_builder(interchange_node: interchange.Concept) -> None:  # noqa: ARG001
    pass


def test_primary_rdf_type() -> None:
    assert isinstance(interchange.Concept.primary_rdf_type(), URIRef)
