from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from pathlib import Path
from typing import IO, TYPE_CHECKING, final, override

import markus
from pathvalidate import sanitize_filename
from rdflib import ConjunctiveGraph, Graph, URIRef
from returns.maybe import Maybe, Nothing

from graphs2go.loaders.buffering_rdf_loader import BufferingRdfLoader
from graphs2go.loaders.directory_loader import DirectoryLoader
from graphs2go.loaders.rdf_loader import RdfLoader

if TYPE_CHECKING:
    from graphs2go.models import rdf


metrics = markus.get_metrics(__name__)


class RdfDirectoryLoader(DirectoryLoader, RdfLoader, ABC):
    """
    Loader that writes RDF graphs to files in a directory on the local file system.

    Graphs with the same identifier are written to the same file.

    The desired RDF format determines whether graphs will be appended/streamed to files as they arrive or buffered in memory
    and written once when the loader is closed. Line-oriented formats such as n-quads and n-triples are preferred for
    large volumes of data because they can be streamed.
    """

    def __init__(
        self,
        *,
        directory_path: Path,
        rdf_format: rdf.Format,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]],
    ):
        DirectoryLoader.__init__(self, directory_path=directory_path)
        self.__rdf_format = rdf_format
        self.__rdf_graph_identifier_to_file_stem: Callable[[URIRef], str] = (
            rdf_graph_identifier_to_file_stem.value_or(
                lambda identifier: sanitize_filename(identifier)
            )
        )

    @classmethod
    def create(
        cls,
        *,
        directory_path: Path,
        rdf_format: rdf.Format,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]] = Nothing,
    ) -> RdfDirectoryLoader:
        if rdf_format.line_oriented:
            return _StreamingRdfDirectoryLoader(
                directory_path=directory_path,
                rdf_format=rdf_format,
                rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
            )
        return _BufferingRdfDirectoryLoader(
            directory_path=directory_path,
            rdf_format=rdf_format,
            rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
        )

    @property
    def _rdf_format(self) -> rdf.Format:
        return self.__rdf_format

    def rdf_graph_file_path(self, identifier: URIRef) -> Path:
        return (
            self._directory_path
            / f"{self.__rdf_graph_identifier_to_file_stem(identifier)}.{self._rdf_format.file_extension}"
        )


@final
class _BufferingRdfDirectoryLoader(BufferingRdfLoader, RdfDirectoryLoader):
    def __init__(
        self,
        *,
        directory_path: Path,
        rdf_format: rdf.Format,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]],
    ):
        BufferingRdfLoader.__init__(
            self,
            default_rdf_graph_type=(
                ConjunctiveGraph if rdf_format.supports_quads else Graph
            ),
        )
        RdfDirectoryLoader.__init__(
            self,
            directory_path=directory_path,
            rdf_format=rdf_format,
            rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
        )

    @override
    def close(self) -> None:
        for stream, graph in self.rdf_graphs_by_identifier.items():
            with metrics.timer("buffered_graph_write"):
                graph.serialize(
                    destination=self.rdf_graph_file_path(stream),
                    encoding="utf-8",
                    format=self._rdf_format.name.lower(),
                )


@final
class _StreamingRdfDirectoryLoader(RdfDirectoryLoader):
    def __init__(
        self,
        *,
        directory_path: Path,
        rdf_format: rdf.Format,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]],
    ):
        RdfDirectoryLoader.__init__(
            self,
            directory_path=directory_path,
            rdf_format=rdf_format,
            rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
        )
        self.__open_files_by_graph_identifier: dict[str, IO[bytes]] = {}
        assert self._rdf_format.line_oriented

    @override
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
                destination=open_file,
                encoding="utf-8",
                format=self._rdf_format.name.lower(),
            )
            open_file.flush()

    @override
    def close(self) -> None:
        for open_file in self.__open_files_by_graph_identifier.values():
            open_file.close()
