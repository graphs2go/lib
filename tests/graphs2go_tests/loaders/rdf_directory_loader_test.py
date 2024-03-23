from pathlib import Path

import pytest
from rdflib import ConjunctiveGraph, Graph, URIRef

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import rdf


@pytest.mark.parametrize(
    argnames=("rdf_graph_type", "rdf_format"),
    argvalues=tuple(
        (rdf_graph_type, rdf_format)
        for rdf_graph_type in (ConjunctiveGraph, Graph)
        for rdf_format in rdf.Format
    ),
)
def test_load(
    rdf_graph_type: type[Graph],
    rdf_graphs: tuple[Graph, ...],
    rdf_format: rdf.Format,
    tmp_path: Path,
) -> None:
    with RdfDirectoryLoader.create(
        directory_path=tmp_path, rdf_format=rdf_format
    ) as loader:
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

    for rdf_graph in rdf_graphs:
        quad_graph = ConjunctiveGraph()
        assert isinstance(rdf_graph.identifier, URIRef)
        quad_graph.parse(loader.rdf_graph_file_path(rdf_graph.identifier))
        assert len(tuple(quad_graph.quads())) == 1
