import pytest

from graphs2go.models import interchange
from graphs2go.namespaces import SKOS
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore


def test_builder(interchange_node: interchange.Node) -> None:
    pass


def test_labels(interchange_node: interchange.Node) -> None:
    assert tuple(interchange_node.labels())


def test_properties(interchange_model_store: InterchangeModelStore) -> None:
    for node in interchange_model_store.nodes():
        for property_ in node.properties():
            assert property_.subject == node.iri
            return
    pytest.fail("no node with properties")


def test_relationships(interchange_model_store: InterchangeModelStore) -> None:
    all_node_iris = {node.iri for node in interchange_model_store.nodes()}
    for node in interchange_model_store.nodes():
        relationships = tuple(node.relationships())
        if not relationships:
            continue
        for relationship in relationships:
            assert relationship.subject == node.iri
            assert relationship.object_ != node.iri
            assert relationship.object_ in all_node_iris
        return
    pytest.fail("didn't find node with relationships")


def test_types(interchange_node: interchange.Node) -> None:
    assert len(interchange_node.types) == 1
    assert interchange_node.types[0] in (SKOS.Concept, SKOS.ConceptScheme)
