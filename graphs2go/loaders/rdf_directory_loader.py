from __future__ import annotations

import bz2
import gzip
from abc import ABC
from typing import IO, TYPE_CHECKING, final, override

import markus
from pathvalidate import sanitize_filename
from rdflib import ConjunctiveGraph, Graph, URIRef
from returns.maybe import Maybe, Nothing
from returns.pipeline import is_successful

from graphs2go.loaders.buffering_rdf_loader import BufferingRdfLoader
from graphs2go.loaders.directory_loader import DirectoryLoader
from graphs2go.loaders.rdf_loader import RdfLoader
from graphs2go.models.compression_method import CompressionMethod
from graphs2go.utils.brotli_file import BrotliFile

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

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

    _OpenRdfGraphFile = BrotliFile | bz2.BZ2File | gzip.GzipFile | IO[bytes]

    def __init__(
        self,
        *,
        directory_path: Path,
        rdf_file_format: rdf.FileFormat,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]],
    ):
        DirectoryLoader.__init__(self, directory_path=directory_path)
        self.__rdf_file_format = rdf_file_format
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
        rdf_file_format: rdf.FileFormat,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]] = Nothing,
    ) -> RdfDirectoryLoader:
        if rdf_file_format.format_.line_oriented:
            return _StreamingRdfDirectoryLoader(
                directory_path=directory_path,
                rdf_file_format=rdf_file_format,
                rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
            )
        return _BufferingRdfDirectoryLoader(
            directory_path=directory_path,
            rdf_file_format=rdf_file_format,
            rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
        )

    def _open_rdf_graph_file(self, identifier: URIRef) -> _OpenRdfGraphFile:
        file_path = self.rdf_graph_file_path(identifier)
        if not is_successful(self.__rdf_file_format.compression_method):
            return file_path.open("w+b")
        file_path.unlink(missing_ok=True)
        match self.__rdf_file_format.compression_method.unwrap():
            case CompressionMethod.BROTLI:
                return BrotliFile(file_path, "wb")
            case CompressionMethod.BZIP2:
                return bz2.BZ2File(file_path, "wb")
            case CompressionMethod.GZIP:
                return gzip.GzipFile(file_path, "wb")
            case _:
                raise NotImplementedError

    @property
    def _rdf_file_format(self) -> rdf.FileFormat:
        return self.__rdf_file_format

    def rdf_graph_file_path(self, identifier: URIRef) -> Path:
        file_name = f"{self.__rdf_graph_identifier_to_file_stem(identifier)}.{self._rdf_file_format.format_.file_extension}"
        if is_successful(self._rdf_file_format.compression_method):
            file_name += "." + (
                self._rdf_file_format.compression_method.unwrap().file_extension
            )
        return self._directory_path / file_name


@final
class _BufferingRdfDirectoryLoader(BufferingRdfLoader, RdfDirectoryLoader):
    def __init__(
        self,
        *,
        directory_path: Path,
        rdf_file_format: rdf.FileFormat,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]],
    ):
        BufferingRdfLoader.__init__(
            self,
            default_rdf_graph_type=(
                ConjunctiveGraph if rdf_file_format.format_.supports_quads else Graph
            ),
        )
        RdfDirectoryLoader.__init__(
            self,
            directory_path=directory_path,
            rdf_file_format=rdf_file_format,
            rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
        )

    @override
    def close(self) -> None:
        for graph_identifier, graph in self.rdf_graphs_by_identifier.items():
            with (
                metrics.timer("buffered_graph_write"),
                self._open_rdf_graph_file(graph_identifier) as file_,
            ):
                graph.serialize(
                    destination=file_,  # type: ignore
                    encoding="utf-8",
                    format=self._rdf_file_format.format_.name.lower(),
                )


@final
class _StreamingRdfDirectoryLoader(RdfDirectoryLoader):
    def __init__(
        self,
        *,
        directory_path: Path,
        rdf_file_format: rdf.FileFormat,
        rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]],
    ):
        RdfDirectoryLoader.__init__(
            self,
            directory_path=directory_path,
            rdf_file_format=rdf_file_format,
            rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
        )
        self.__open_files_by_graph_identifier: dict[
            str, RdfDirectoryLoader._OpenRdfGraphFile
        ] = {}
        assert self._rdf_file_format.format_.line_oriented

    @override
    def load(self, rdf_graph: Graph) -> None:
        if not isinstance(rdf_graph.identifier, URIRef):
            raise ValueError("graph must have a named identifier")  # noqa: TRY004

        open_file = self.__open_files_by_graph_identifier.get(rdf_graph.identifier)
        if open_file is None:
            open_file = self.__open_files_by_graph_identifier[rdf_graph.identifier] = (
                self._open_rdf_graph_file(rdf_graph.identifier)
            )

        with metrics.timer("streaming_graph_write"):
            serializable_graph: Graph
            if self._rdf_file_format.format_.supports_quads:
                if isinstance(rdf_graph, ConjunctiveGraph):
                    serializable_graph = rdf_graph
                else:
                    serializable_graph = ConjunctiveGraph()
                    for triple in rdf_graph:
                        serializable_graph.add(triple)
            else:
                serializable_graph = rdf_graph

            serializable_graph.serialize(
                destination=open_file,  # type: ignore
                encoding="utf-8",
                format=self._rdf_file_format.format_.name.lower(),
            )
            open_file.flush()

    @override
    def close(self) -> None:
        for open_file in self.__open_files_by_graph_identifier.values():
            open_file.close()
