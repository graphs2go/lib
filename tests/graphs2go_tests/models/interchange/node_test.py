import pytest
from rdflib import URIRef

from graphs2go.models import interchange


def test_builder(interchange_node: interchange.Node) -> None:  # noqa: ARG001
    pass


def test_labels(interchange_node: interchange.Node) -> None:
    assert tuple(interchange_node.labels)


def test_properties(interchange_graph: interchange.Graph) -> None:
    for node in interchange_graph.nodes():
        for property_ in node.properties:
            assert property_.subject == node.uri
            return
    pytest.fail("no node with properties")


def test_relationships(interchange_graph: interchange.Graph) -> None:
    all_node_uris = {node.uri for node in interchange_graph.nodes()}
    for node in interchange_graph.nodes():
        relationships = tuple(node.relationships)
        if not relationships:
            continue
        for relationship in relationships:
            assert relationship.subject == node.uri
            assert relationship.object != node.uri
            assert relationship.object in all_node_uris
        return
    pytest.fail("didn't find node with relationships")


def test_primary_rdf_type() -> None:
    assert isinstance(interchange.Node.primary_rdf_type(), URIRef)
