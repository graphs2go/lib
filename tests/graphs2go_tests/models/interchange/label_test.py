from rdflib import Literal, URIRef

from graphs2go.models import interchange


def test_builder(interchange_label: interchange.Label) -> None:  # noqa: ARG001
    pass


def test_literal_form(interchange_label: interchange.Label) -> None:
    assert isinstance(interchange_label.literal_form, Literal)


def test_rdf_type_uri() -> None:
    assert isinstance(interchange.Label.rdf_type_uri(), URIRef)
