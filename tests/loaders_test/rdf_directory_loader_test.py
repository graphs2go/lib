from pathlib import Path
import pytest

from rdflib import ConjunctiveGraph, Graph
from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.loaders.rdf_format import RdfFormat

from graphs2go.loaders.rdf_graph_record import RdfGraphRecord


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
    rdf_graph_records: tuple[RdfGraphRecord, ...],
    rdf_format: RdfFormat,
    tmp_path: Path,
) -> None:
    with RdfDirectoryLoader.create(
        directory_path=tmp_path, rdf_format=rdf_format
    ) as loader:
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

    for rdf_graph_record in rdf_graph_records:
        quad_graph = ConjunctiveGraph()
        quad_graph.parse(tmp_path / (f"{rdf_graph_record.stream}.{rdf_format}"))
        assert len(tuple(quad_graph.quads())) == 1
