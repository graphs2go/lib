from rdflib import URIRef

from graphs2go.models import interchange


def test_builder(
    interchange_relationship: interchange.Relationship,  # noqa: ARG001
) -> None:
    pass


def test_object(
    interchange_graph: interchange.Graph,
    interchange_relationship: interchange.Relationship,
) -> None:
    assert isinstance(interchange_relationship.object, URIRef)
    assert interchange_relationship.subject in {
        node.uri for node in interchange_graph.nodes
    }


def test_predicate(interchange_relationship: interchange.Relationship) -> None:
    assert isinstance(interchange_relationship.predicate, URIRef)


def test_primary_rdf_type() -> None:
    assert isinstance(interchange.Relationship.primary_rdf_type(), URIRef)


def test_subject(
    interchange_graph: interchange.Graph,
    interchange_relationship: interchange.Relationship,
) -> None:
    assert isinstance(interchange_relationship.subject, URIRef)
    assert interchange_relationship.subject in {
        node.uri for node in interchange_graph.nodes
    }
