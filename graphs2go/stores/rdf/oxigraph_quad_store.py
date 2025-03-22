from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, IO

import pyoxigraph
import pyoxigraph as ox

from graphs2go.models.rdf import Quad
from graphs2go.stores.rdf.quad_store import QuadStore
from returns.maybe import Maybe

from graphs2go.models.rdf.oxigraph_adapters import OxigraphAdapters

if TYPE_CHECKING:
    from graphs2go.models import rdf
    from collections.abc import Iterable
    from pathlib import Path


class OxigraphQuadStore(QuadStore):
    """
    A store backed by Oxigraph, either in-memory or on disk.

    Adapted from oxrdflib.
    """

    @dataclass(frozen=True)
    class Descriptor(QuadStore.Descriptor):
        directory_path: Path
        transactional: bool

    def __init__(self, *, directory_path: Path, read_only: bool, transactional: bool):
        self.__directory_path = directory_path
        if read_only:
            if not self.__directory_path.is_dir():
                raise ValueError(
                    "store opened read-only but directory %s does not exist or is not a directory",
                    self.__directory_path,
                )
            self.__delegate = ox.Store.read_only(str(self.__directory_path))
        else:
            self.__directory_path.mkdir(exist_ok=True, parents=True)
            self.__delegate = ox.Store(self.__directory_path)
        self.__transactional = transactional

    def add(self, quad: rdf.Quad) -> None:
        self.__delegate.add(OxigraphAdapters.Quad.to_ox(quad))

    def close(self) -> None:  # noqa: ARG002
        # There's no explicit close on the pyoxigraph Store.
        # Delete all references to the pyoxigraph Store so it gets garbage collected and releases its lock.
        with contextlib.suppress(AttributeError):
            del self.__delegate

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            directory_path=self.__directory_path,
            transactional=self.__transactional,
        )

    def _dump(
        self, *, format_: rdf.Format, output: IO[bytes], prefixes: dict[str, rdf.Iri]
    ) -> None:
        self.__delegate.dump(
            format=pyoxigraph.RdfFormat.from_extension(format_.file_extension),
            from_graph=None if format_.supports_quads else ox.DefaultGraph(),
            prefixes={prefix: str(namespace) for prefix, namespace in prefixes.items()},
            output=output,
        )

    def extend(self, quads: Iterable[rdf.Quad]) -> None:
        if self.__transactional:
            self.__delegate.extend(OxigraphAdapters.Quad.to_ox(quad) for quad in quads)  # type: ignore
        else:
            self.__delegate.bulk_extend(OxigraphAdapters.Quad.to_ox(quad) for quad in quads)  # type: ignore

    def _load(self, *, format_: rdf.Format, input_: IO[bytes] | IO[str]) -> None:
        if self.__transactional:
            self.__delegate.load(
                input=input_,
                format=pyoxigraph.RdfFormat.from_extension(format_.file_extension),
            )
        else:
            self.__delegate.bulk_load(
                input=input_,
                format=pyoxigraph.RdfFormat.from_extension(format_.file_extension),
            )

    def match(
        self,
        subject: rdf.Quad_Subject | None = None,
        predicate: rdf.Quad_Predicate | None = None,
        object_: rdf.Quad_Object | None = None,
        graph: rdf.Quad_Graph = None,
    ) -> Iterable[rdf.Quad]:
        for quad in self.__delegate.quads_for_pattern(
            (
                OxigraphAdapters.Quad.Subject.to_ox(subject)
                if subject is not None
                else None
            ),
            (
                OxigraphAdapters.Quad.Predicate.to_ox(predicate)
                if predicate is not None
                else None
            ),
            (
                OxigraphAdapters.Quad.Object.to_ox(object_)
                if object_ is not None
                else None
            ),
            OxigraphAdapters.Quad.Graph.to_ox(graph) if graph is not None else None,
        ):
            yield OxigraphAdapters.Quad.from_ox(quad)

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> QuadStore:
        return OxigraphQuadStore(
            directory_path=descriptor.directory_path,
            read_only=read_only,
            transactional=descriptor.transactional,
        )

    def remove(self, quad: Quad) -> None:
        self.__delegate.remove(OxigraphAdapters.Quad.to_ox(quad))
