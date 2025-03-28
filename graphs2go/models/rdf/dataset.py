from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from io import BytesIO, StringIO
from pathlib import Path
from typing import IO

from graphs2go.models.rdf.namespace_prefixes import NamespacePrefixes
from graphs2go.models.rdf.format import Format
from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.quad import (
    Quad,
    Quad_Graph,
    Quad_Object,
    Quad_Predicate,
    Quad_Subject,
)


class Dataset(ABC, Iterable[Quad]):
    """
    Abstract base class/interface over an RDF dataset (https://www.w3.org/TR/rdf11-datasets/).

    Loosely modeled on Oxigraph's Dataset class (https://pyoxigraph.readthedocs.io/en/stable/model.html#pyoxigraph.Dataset).

    A QuadStore is a persistent implementation of a Dataset.
    """

    @abstractmethod
    def add(self, quad: Quad) -> None:
        """
        Add a quad to the Dataset.
        """

        raise NotImplementedError

    def clear(self) -> None:
        """
        Clear all quads from the Dataset.
        """

        for quad in self.match():
            self.remove(quad)

    def count_matches(
        self,
        subject: Quad_Subject | None = None,
        predicate: Quad_Predicate | None = None,
        object_: Quad_Object | None = None,
        graph: Quad_Graph = None,
    ) -> int:
        """
        Count all matching quads from the Dataset.

        The parameters have the same semantics as match.
        """

        count = 0
        for _ in self.match(subject, predicate, object_, graph):
            count += 1
        return count

    def dump(
        self,
        *,
        format_: Format,
        namespace_prefixes: NamespacePrefixes | None = None,
        output: IO[bytes] | Path | None = None,
    ) -> bytes | None:
        if isinstance(output, Path):
            with output.open("wb") as file_output:
                self._dump(
                    format_=format_,
                    namespace_prefixes=namespace_prefixes or {},
                    output=file_output,
                )
                return None
        elif output is None:
            with BytesIO() as bytes_output:
                self._dump(
                    format_=format_,
                    namespace_prefixes=namespace_prefixes or {},
                    output=bytes_output,
                )
                return bytes_output.getvalue()
        else:
            self._dump(
                format_=format_,
                output=output,
                namespace_prefixes=namespace_prefixes or {},
            )
            return None

    @abstractmethod
    def _dump(
        self,
        *,
        format_: Format,
        output: IO[bytes],
        namespace_prefixes: dict[str, Iri],
    ) -> None:
        raise NotImplementedError

    def extend(self, quads: Iterable[Quad]) -> None:
        """
        Add zero or more quads to the Dataset.
        """

        for quad in quads:
            self.add(quad)

    @property
    def is_empty(self) -> bool:
        """
        Check if the Dataset has quads or not.
        """

        for _ in self.match():
            return False
        return True

    def __len__(self) -> int:
        """
        The number of quads in the Dataset.
        """

        count = 0
        for _ in self.match():
            count += 1
        return count

    def __iter__(self) -> Iterator[Quad]:
        yield from self.match()

    def load(
        self, *, format_: Format, input_: bytes | IO[bytes] | IO[str] | Path | str
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
    def _load(self, *, format_: Format, input_: IO[bytes] | IO[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def match(
        self,
        subject: Quad_Subject | None = None,
        predicate: Quad_Predicate | None = None,
        object_: Quad_Object | None = None,
        graph: Quad_Graph = None,
    ) -> Iterable[Quad]:
        """
        Return matching quads in the Dataset.

        If subject is specified, return all quads with that exact subject.
        If subject is unspecified, return quads with any subjects.
        Similar for predicate, object, graph.
        Combinations of parameters are conjunctive (subject = X and predicate = Y).
        """

        raise NotImplementedError

    @abstractmethod
    def remove(self, quad: Quad) -> None:
        """
        Remove a quad from the Dataset.
        """

        raise NotImplementedError

    def remove_matches(
        self,
        subject: Quad_Subject | None = None,
        predicate: Quad_Predicate | None = None,
        object_: Quad_Object | None = None,
        graph: Quad_Graph = None,
    ) -> None:
        """
        Remove all matching quads from the Dataset.

        The parameters have the same semantics as match.
        """

        for quad in self.match(subject, predicate, object_, graph):
            self.remove(quad)
