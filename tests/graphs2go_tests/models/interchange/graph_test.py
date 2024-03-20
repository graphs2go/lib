from graphs2go.models import interchange


def test_concepts(interchange_graph: interchange.Graph) -> None:
    concepts = tuple(interchange_graph.concepts)
    assert concepts
    assert all(isinstance(concept, interchange.Concept) for concept in concepts)


def test_nodes(interchange_graph: interchange.Graph) -> None:
    assert tuple(interchange_graph.nodes)
