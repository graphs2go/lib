from __future__ import annotations

from pathlib import Path
from typing import IO, TYPE_CHECKING

import markus
from pathvalidate import sanitize_filename
from rdflib import ConjunctiveGraph, Graph, URIRef

from graphs2go.loaders.buffering_rdf_loader import BufferingRdfLoader
from graphs2go.loaders.directory_loader import DirectoryLoader
from graphs2go.loaders.rdf_loader import RdfLoader

if TYPE_CHECKING:
    from graphs2go.models.rdf_format import RdfFormat


metrics = markus.get_metrics(__name__)


class RdfDirectoryLoader(DirectoryLoader, RdfLoader):
    def __init__(self, *, directory_path: Path, rdf_format: RdfFormat):
        DirectoryLoader.__init__(self, directory_path=directory_path)
        self.__rdf_format = rdf_format

    @classmethod
    def create(
        cls, *, directory_path: Path, rdf_format: RdfFormat
    ) -> RdfDirectoryLoader:
        if rdf_format.line_oriented:
            return _StreamingRdfDirectoryLoader(
                directory_path=directory_path, rdf_format=rdf_format
            )
        return _BufferingRdfDirectoryLoader(
            directory_path=directory_path, rdf_format=rdf_format
        )

    @property
    def _rdf_format(self) -> RdfFormat:
        return self.__rdf_format

    def rdf_graph_file_path(self, identifier: URIRef) -> Path:
        return (
            self._directory_path / f"{sanitize_filename(identifier)}.{self._rdf_format}"
        )


class _BufferingRdfDirectoryLoader(BufferingRdfLoader, RdfDirectoryLoader):
    def __init__(self, *, directory_path: Path, rdf_format: RdfFormat):
        BufferingRdfLoader.__init__(
            self,
            default_rdf_graph_type=(
                ConjunctiveGraph if rdf_format.supports_quads else Graph
            ),
        )
        RdfDirectoryLoader.__init__(
            self, directory_path=directory_path, rdf_format=rdf_format
        )

    def close(self) -> None:
        for stream, graph in self.rdf_graphs_by_identifier.items():
            with metrics.timer("buffered_graph_write"):
                graph.serialize(
                    destination=self.rdf_graph_file_path(stream),
                    format=str(self._rdf_format),
                )


class _StreamingRdfDirectoryLoader(RdfDirectoryLoader):
    def __init__(self, *, directory_path: Path, rdf_format: RdfFormat):
        RdfDirectoryLoader.__init__(
            self, directory_path=directory_path, rdf_format=rdf_format
        )
        self.__open_files_by_graph_identifier: dict[str, IO[bytes]] = {}
        assert self._rdf_format.line_oriented

    def load(self, rdf_graph: Graph) -> None:
        if not isinstance(rdf_graph.identifier, URIRef):
            raise ValueError("graph must have a named identifier")  # noqa: TRY004

        open_file = self.__open_files_by_graph_identifier.get(rdf_graph.identifier)
        if open_file is None:
            open_file = self.__open_files_by_graph_identifier[rdf_graph.identifier] = (
                Path.open(
                    self.rdf_graph_file_path(rdf_graph.identifier),
                    "w+b",
                )
            )

        with metrics.timer("streaming_graph_write"):
            serializable_graph: Graph
            if self._rdf_format.supports_quads:
                if isinstance(rdf_graph, ConjunctiveGraph):
                    serializable_graph = rdf_graph
                else:
                    serializable_graph = ConjunctiveGraph()
                    for triple in rdf_graph:
                        serializable_graph.add(triple)
            else:
                serializable_graph = rdf_graph

            serializable_graph.serialize(
                destination=open_file, format=str(self._rdf_format)
            )
            open_file.flush()

    def close(self) -> None:
        for open_file in self.__open_files_by_graph_identifier.values():
            open_file.close()
