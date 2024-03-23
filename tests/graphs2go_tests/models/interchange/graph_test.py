from graphs2go.models import interchange


def test_nodes(interchange_graph: interchange.Graph) -> None:
    assert tuple(interchange_graph.nodes())
