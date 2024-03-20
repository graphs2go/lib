import pytest
from rdflib import URIRef
from graphs2go.models import interchange


def test_builder(interchange_node: interchange.Node) -> None:  # noqa: ARG001
    pass


def test_labels(
    interchange_node: interchange.Concept,
    interchange_concept_label: interchange.Label,
) -> None:
    assert tuple(label.uri for label in interchange_node.labels) == (
        interchange_concept_label.uri,
    )


def test_properties(interchange_node: interchange.Concept) -> None:
    properties = tuple(interchange_node.properties)
    assert properties
    for property_ in properties:
        assert property_.subject == interchange_node.uri


def test_relationships(interchange_graph: interchange.Graph) -> None:
    all_node_uris = {node.uri for node in interchange_graph.nodes}
    for node in interchange_graph.nodes:
        relationships = tuple(node.relationships)
        if not relationships:
            continue
        for relationship in relationships:
            assert relationship.subject == node.uri
            assert relationship.object_ != node.uri
            assert relationship.object_ in all_node_uris
        return
    pytest.fail("didn't find node with relationships")


def test_rdf_type_uri() -> None:
    assert isinstance(interchange.Node.rdf_type_uri(), URIRef)
