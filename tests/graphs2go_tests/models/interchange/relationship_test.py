from rdflib import URIRef
from graphs2go.models import interchange


def test_builder(
    interchange_relationship: interchange.Relationship,  # noqa: ARG001
) -> None:
    pass


def test_rdf_type_uri() -> None:
    assert isinstance(interchange.Relationship.rdf_type_uri(), URIRef)
