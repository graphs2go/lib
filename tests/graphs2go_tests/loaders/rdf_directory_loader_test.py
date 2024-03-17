from pathlib import Path

import pytest
from rdflib import ConjunctiveGraph, Graph

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models.rdf_format import RdfFormat
from graphs2go.models.loadable_rdf_graph import LoadableRdfGraph


@pytest.mark.parametrize(
    argnames=("rdf_graph_type", "rdf_format"),
    argvalues=tuple(
        (rdf_graph_type, rdf_format)
        for rdf_graph_type in (ConjunctiveGraph, Graph)
        for rdf_format in RdfFormat
    ),
)
def test_load(
    rdf_graph_type: type[Graph],
    loadable_rdf_graphs: tuple[LoadableRdfGraph, ...],
    rdf_format: RdfFormat,
    tmp_path: Path,
) -> None:
    with RdfDirectoryLoader.create(
        directory_path=tmp_path, rdf_format=rdf_format
    ) as loader:
        for loadable_rdf_graph in loadable_rdf_graphs:
            assert not isinstance(loadable_rdf_graph, ConjunctiveGraph)
            if rdf_graph_type == ConjunctiveGraph:
                quad_graph = ConjunctiveGraph()
                for triple in loadable_rdf_graph.graph:
                    quad_graph.add(triple)
                loader(
                    LoadableRdfGraph(graph=quad_graph, stream=loadable_rdf_graph.stream)
                )
            else:
                assert rdf_graph_type == Graph
                loader(loadable_rdf_graph)

    for loadable_rdf_graph in loadable_rdf_graphs:
        quad_graph = ConjunctiveGraph()
        quad_graph.parse(tmp_path / (f"{loadable_rdf_graph.stream}.{rdf_format}"))
        assert len(tuple(quad_graph.quads())) == 1
