import pytest
from rdflib import ConjunctiveGraph, Graph

from graphs2go.loaders.buffering_rdf_loader import BufferingRdfLoader


@pytest.mark.parametrize(
    argnames=("rdf_graph_type",),
    argvalues=tuple((rdf_graph_type,) for rdf_graph_type in (ConjunctiveGraph, Graph)),
)
def test_load(
    rdf_graph_type: type[Graph],
    rdf_graphs: tuple[Graph, ...],
) -> None:
    loader = BufferingRdfLoader(default_rdf_graph_type=rdf_graph_type)
    for rdf_graph in rdf_graphs:
        assert not isinstance(rdf_graph, ConjunctiveGraph)
        if rdf_graph_type == ConjunctiveGraph:
            quad_graph = ConjunctiveGraph(identifier=rdf_graph.identifier)
            for triple in rdf_graph:
                quad_graph.add(triple)
            loader.load(quad_graph)
        else:
            assert rdf_graph_type == Graph
            loader.load(rdf_graph)

    assert len(loader.rdf_graphs_by_identifier) == 2
    for graph in loader.rdf_graphs_by_identifier.values():
        assert graph
