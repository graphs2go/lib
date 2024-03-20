from rdflib import URIRef
from graphs2go.models import interchange


def test_builder(
    interchange_property: interchange.Property,  # noqa: ARG001
) -> None:
    pass


def test_rdf_type_uri() -> None:
    assert isinstance(interchange.Property.rdf_type_uri(), URIRef)
