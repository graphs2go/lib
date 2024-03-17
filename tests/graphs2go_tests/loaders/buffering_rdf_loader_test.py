import pytest
from rdflib import ConjunctiveGraph, Graph

from graphs2go.loaders.buffering_rdf_loader import BufferingRdfLoader
from graphs2go.models.loadable_rdf_graph import LoadableRdfGraph


@pytest.mark.parametrize(
    argnames=("rdf_graph_type",),
    argvalues=tuple((rdf_graph_type,) for rdf_graph_type in (ConjunctiveGraph, Graph)),
)
def test_load(
    rdf_graph_type: type[Graph],
    loadable_rdf_graphs: tuple[LoadableRdfGraph, ...],
) -> None:
    loader = BufferingRdfLoader(default_rdf_graph_type=rdf_graph_type)
    for loadable_rdf_graph in loadable_rdf_graphs:
        assert not isinstance(loadable_rdf_graph, ConjunctiveGraph)
        if rdf_graph_type == ConjunctiveGraph:
            quad_graph = ConjunctiveGraph()
            for triple in loadable_rdf_graph.graph:
                quad_graph.add(triple)
            loader(LoadableRdfGraph(graph=quad_graph, stream=loadable_rdf_graph.stream))
        else:
            assert rdf_graph_type == Graph
            loader(loadable_rdf_graph)

    assert len(loader.rdf_graphs_by_stream) == 2
    for graph in loader.rdf_graphs_by_stream.values():
        assert graph
