from __future__ import annotations

import bz2
import gzip
from abc import ABC, abstractmethod
from typing import IO, TYPE_CHECKING, final, override

import markus
from returns.maybe import Maybe, Nothing
from returns.pipeline import is_successful

from graphs2go.models import CompressionMethod, rdf
from graphs2go.models.rdf.oxigraph_dataset import OxigraphDataset
from graphs2go.namespaces import NAMESPACE_PREFIXES
from graphs2go.utils.brotli_file import BrotliFile

if TYPE_CHECKING:
    from pathlib import Path


metrics = markus.get_metrics(__name__)


class FileLoader(ABC):
    """
    Loader that writes RDF graphs to a file.

    The desired RDF format determines whether graphs will be appended/streamed to files as they arrive or buffered in memory
    and written once when the loader is closed. Line-oriented formats such as n-quads and n-triples are preferred for
    large volumes of data because they can be streamed.
    """

    _OpenFile = BrotliFile | bz2.BZ2File | gzip.GzipFile | IO[bytes]

    def __init__(
        self,
        *,
        file_format: rdf.FileFormat,
        file_path: Path,
        namespace_prefixes: Maybe[dict[str, rdf.Iri]],
    ):
        self.__file_path = file_path
        self.__file_format = file_format
        self.__prefixes = namespace_prefixes.value_or(NAMESPACE_PREFIXES)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @abstractmethod
    def close(self) -> None:
        pass

    @classmethod
    def create(
        cls,
        *,
        file_format: rdf.FileFormat,
        file_path: Path,
        namespace_prefixes: Maybe[rdf.NamespacePrefixes] = Nothing,
    ) -> FileLoader:
        if file_format.format_.line_oriented:
            return _StreamingFileLoader(
                file_path=file_path,
                file_format=file_format,
                namespace_prefixes=namespace_prefixes,
            )
        return _BufferingFileLoader(
            file_format=file_format,
            file_path=file_path,
            namespace_prefixes=namespace_prefixes,
        )

    @abstractmethod
    def load(self, dataset: rdf.Dataset) -> None:
        pass

    def _open_file(self) -> _OpenFile:
        if not is_successful(self.__file_format.compression_method):
            return self.__file_path.open("w+b")
        self.__file_path.unlink(missing_ok=True)
        match self.__file_format.compression_method.unwrap():
            case CompressionMethod.BROTLI:
                return BrotliFile(self.__file_path, "wb")
            case CompressionMethod.BZIP2:
                return bz2.BZ2File(self.__file_path, "wb")
            case CompressionMethod.GZIP:
                return gzip.GzipFile(self.__file_path, "wb")
            case _:
                raise NotImplementedError

    @property
    def _file_format(self) -> rdf.FileFormat:
        return self.__file_format


@final
class _BufferingFileLoader(FileLoader):
    def __init__(
        self,
        *,
        file_format: rdf.FileFormat,
        file_path: Path,
        namespace_prefixes: Maybe[dict[str, rdf.Iri]],
    ):
        FileLoader.__init__(
            self,
            file_path=file_path,
            file_format=file_format,
            namespace_prefixes=namespace_prefixes,
        )
        self.__buffered_dataset = OxigraphDataset()

    @override
    def close(self) -> None:
        with metrics.timer("buffered_dataset_write"), self._open_file() as file_:
            self.__buffered_dataset.dump(
                format_=self._file_format.format_,
                output=file_,  # type: ignore
            )

    def load(self, dataset: rdf.Dataset) -> None:
        self.__buffered_dataset.extend(dataset)


@final
class _StreamingFileLoader(FileLoader):
    def __init__(
        self,
        *,
        file_format: rdf.FileFormat,
        file_path: Path,
        namespace_prefixes: Maybe[dict[str, rdf.Iri]],
    ):
        FileLoader.__init__(
            self,
            file_format=file_format,
            file_path=file_path,
            namespace_prefixes=namespace_prefixes,
        )
        assert self._file_format.format_.line_oriented
        self.__open_file: FileLoader._OpenFile | None = None

    @override
    def load(self, dataset: rdf.Dataset) -> None:
        if self.__open_file is None:
            self.__open_file = self._open_file()

        with metrics.timer("streaming_dataset_write"):
            dataset.dump(
                format_=self._file_format.format_,
                output=self.__open_file,  # type: ignore
            )
            self.__open_file.flush()

    @override
    def close(self) -> None:
        if self.__open_file is not None:
            self.__open_file.close()
