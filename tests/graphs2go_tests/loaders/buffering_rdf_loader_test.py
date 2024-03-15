import pytest
from rdflib import ConjunctiveGraph, Graph

from graphs2go.loaders.buffering_rdf_loader import BufferingRdfLoader
from graphs2go.models.rdf_graph_record import RdfGraphRecord


@pytest.mark.parametrize(
    argnames=("rdf_graph_type",),
    argvalues=tuple((rdf_graph_type,) for rdf_graph_type in (ConjunctiveGraph, Graph)),
)
def test_load(
    rdf_graph_type: type[Graph],
    rdf_graph_records: tuple[RdfGraphRecord, ...],
) -> None:
    loader = BufferingRdfLoader(default_rdf_graph_type=rdf_graph_type)
    for rdf_graph_record in rdf_graph_records:
        assert not isinstance(rdf_graph_record, ConjunctiveGraph)
        if rdf_graph_type == ConjunctiveGraph:
            quad_graph = ConjunctiveGraph()
            for triple in rdf_graph_record.graph:
                quad_graph.add(triple)
            loader(RdfGraphRecord(graph=quad_graph, stream=rdf_graph_record.stream))
        else:
            assert rdf_graph_type == Graph
            loader(rdf_graph_record)

    assert len(loader.rdf_graphs_by_stream) == 2
    for graph in loader.rdf_graphs_by_stream.values():
        assert graph
