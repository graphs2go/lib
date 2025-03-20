from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO, StringIO
from typing import TYPE_CHECKING, Self, IO

from returns.maybe import Maybe
from returns.pipeline import is_successful

from graphs2go.models import rdf
from pathlib import Path

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class Store(ABC):
    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

    @abstractmethod
    def add(self, quad: rdf.Quad) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> Self:
        raise NotImplementedError()

    @staticmethod
    def create(*, config: RdfStoreConfig) -> Store:
        config_parsed = config.parse()

        from .oxigraph_store import OxigraphStore

        if not is_successful(config_parsed.directory_path):
            return OxigraphStore(directory_path=Maybe.empty)

        oxigraph_directory_path = config_parsed.directory_path.unwrap()
        oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphStore(
            directory_path=oxigraph_directory_path,
            read_only=False,
            transactional=config_parsed.transactional,
        )

    @property
    @abstractmethod
    def descriptor(self) -> Descriptor:
        pass

    def dump(
        self,
        *,
        format_: rdf.Format,
        output: IO[bytes] | Path | None = None,
        prefixes: dict[str, rdf.Iri] | None = None,
    ) -> bytes | None:
        if isinstance(output, Path):
            with output.open("wb") as file_output:
                self._dump(format_=format_, output=file_output, prefixes=prefixes or {})
                return None
        elif output is None:
            with BytesIO() as bytes_output:
                self._dump(
                    format_=format_, output=bytes_output, prefixes=prefixes or {}
                )
                return bytes_output.getvalue()
        else:
            self._dump(format_=format_, output=output, prefixes=prefixes or {})
            return None

    @abstractmethod
    def _dump(
        self,
        *,
        format_: rdf.Format,
        output: IO[bytes],
        prefixes: dict[str, rdf.Iri],
    ) -> None:
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    def extend(self, quads: Iterable[rdf.Quad]) -> None:
        for quad in quads:
            self.add(quad)

    @property
    def is_empty(self) -> bool:
        for _ in self.match():
            return False
        return True

    def __len__(self) -> int:
        count = 0
        for _ in self.match():
            count += 1
        return count

    def load(
        self, *, format_: rdf.Format, input_: bytes | IO[bytes] | IO[str] | Path | str
    ) -> None:
        if isinstance(input_, bytes):
            with BytesIO(input_) as bytes_input:
                self._load(format_=format_, input_=bytes_input)
        elif isinstance(input_, Path):
            with input_.open("rb") as file_input:
                self._load(format_=format_, input_=file_input)
        elif isinstance(input_, str):
            with StringIO(input_) as str_input:
                self._load(format_=format_, input_=str_input)
        else:
            self._load(format_=format_, input_=input_)

    @abstractmethod
    def _load(self, *, format_: rdf.Format, input_: IO[bytes] | IO[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def match(
        self,
        subject: rdf.Quad_Subject | None = None,
        predicate: rdf.Quad_Predicate | None = None,
        object_: rdf.Quad_Object | None = None,
        graph: rdf.Quad_Graph = None,
    ) -> Iterable[rdf.Quad]:
        raise NotImplementedError

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> Store:
        from .oxigraph_store import OxigraphStore

        if isinstance(descriptor, OxigraphStore.Descriptor):
            return OxigraphStore.open(descriptor, read_only=read_only)

        raise TypeError(type(descriptor))
