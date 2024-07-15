from pathlib import Path

import pytest
from rdflib import ConjunctiveGraph, Graph, URIRef
from returns.maybe import Nothing, Some
from returns.pipeline import is_successful

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import rdf
from graphs2go.models.compression_method import CompressionMethod


@pytest.mark.parametrize(
    argnames=("rdf_graph_type", "rdf_file_format"),
    argvalues=tuple(
        (
            rdf_graph_type,
            rdf.FileFormat(rdf_format, compression_method=compression_method),
        )
        for rdf_graph_type in (ConjunctiveGraph, Graph)
        for rdf_format in rdf.Format
        for compression_method in (
            Nothing,
            *(Some(compression_method) for compression_method in CompressionMethod),
        )
    ),
)
def test_load(
    rdf_file_format: rdf.FileFormat,
    rdf_graph_type: type[Graph],
    rdf_graphs: tuple[Graph, ...],
    tmp_path: Path,
) -> None:
    with RdfDirectoryLoader.create(
        directory_path=tmp_path, rdf_file_format=rdf_file_format
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

    if not is_successful(rdf_file_format.compression_method):
        for rdf_graph in rdf_graphs:
            quad_graph = ConjunctiveGraph()
            assert isinstance(rdf_graph.identifier, URIRef)
            quad_graph.parse(loader.rdf_graph_file_path(rdf_graph.identifier))
            assert len(tuple(quad_graph.quads())) == 1
    else:
        assert loader.rdf_graph_file_path(rdf_graph.identifier).is_file()
