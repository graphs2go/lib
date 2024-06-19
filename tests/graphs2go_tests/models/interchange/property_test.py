from rdflib import Literal, URIRef

from graphs2go.models import interchange


def test_builder(
    interchange_property: interchange.Property,  # noqa: ARG001
) -> None:
    pass


def test_object(interchange_property: interchange.Property) -> None:
    assert isinstance(interchange_property.object, Literal)


def test_predicate(interchange_property: interchange.Property) -> None:
    assert isinstance(interchange_property.predicate, URIRef)


def test_primary_rdf_type() -> None:
    assert isinstance(interchange.Property.primary_rdf_type(), URIRef)


def test_subject(
    interchange_graph: interchange.Graph, interchange_property: interchange.Property
) -> None:
    assert isinstance(interchange_property.subject, URIRef)
    assert interchange_property.subject in {
        node.iri for node in interchange_graph.nodes()
    }
