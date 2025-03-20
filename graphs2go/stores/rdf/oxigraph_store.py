from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, IO

import pyoxigraph
import pyoxigraph as ox

from graphs2go.models import rdf
from .store import Store
from returns.maybe import Maybe

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


def _literal_from_ox(literal: ox.Literal) -> rdf.Literal:
    if literal.language:
        return rdf.Literal(literal.value, lang=literal.language)
    return rdf.Literal(literal.value, datatype=rdf.Literal(literal.datatype.value))


def _literal_to_ox(literal: rdf.Literal) -> ox.Literal:
    return ox.Literal(
        literal,
        language=literal.language,
        datatype=ox.NamedNode(literal.datatype) if literal.datatype else None,
    )


def _quad_from_ox(quad: ox.Quad) -> rdf.Quad:
    return rdf.Quad(
        _quad_subject_from_ox(quad.subject),
        _quad_predicate_from_ox(quad.predicate),
        _quad_object_from_ox(quad.object),
        _quad_graph_from_ox(quad.graph_name),
    )


def _quad_graph_from_ox(
    graph: ox.BlankNode | ox.DefaultGraph | ox.NamedNode,
) -> rdf.Quad_Graph:
    if isinstance(graph, ox.BlankNode):
        return rdf.BlankNode(graph.value)
    if isinstance(graph, ox.DefaultGraph):
        return None
    if isinstance(graph, ox.NamedNode):
        return rdf.Iri(graph.value)
    raise TypeError(type(graph))


def _quad_graph_to_ox(
    graph: rdf.Quad_Graph,
) -> ox.BlankNode | ox.DefaultGraph | ox.NamedNode:
    if graph is None:
        return ox.DefaultGraph()
    if isinstance(graph, rdf.BlankNode):
        return ox.BlankNode(graph)
    if isinstance(graph, rdf.Iri):
        return ox.NamedNode(graph)
    raise TypeError(type(graph))


def _quad_object_from_ox(
    object_: ox.BlankNode | ox.Literal | ox.NamedNode | ox.Triple,
) -> rdf.Quad_Object:
    if isinstance(object_, ox.BlankNode):
        return rdf.BlankNode(object_.value)
    if isinstance(object_, ox.Literal):
        return _literal_from_ox(object_)
    if isinstance(object_, ox.NamedNode):
        return rdf.Iri(object_.value)
    raise TypeError(type(object_))


def _quad_object_to_ox(
    object_: rdf.Quad_Object,
) -> ox.BlankNode | ox.Literal | ox.NamedNode:
    if isinstance(object_, rdf.BlankNode):
        return ox.BlankNode(object_)
    if isinstance(object_, rdf.Literal):
        return _literal_to_ox(object_)
    if isinstance(object_, rdf.Iri):
        return ox.NamedNode(object_)
    raise TypeError(type(object_))


def _quad_predicate_from_ox(predicate: ox.NamedNode) -> rdf.Iri:
    return rdf.Iri(predicate.value)


def _quad_predicate_to_ox(predicate: rdf.Quad_Predicate) -> ox.NamedNode:
    return ox.NamedNode(predicate)


def _quad_subject_from_ox(
    subject: ox.BlankNode | ox.NamedNode | ox.Triple,
) -> rdf.Quad_Subject:
    if isinstance(subject, ox.BlankNode):
        return rdf.BlankNode(subject.value)
    if isinstance(subject, ox.NamedNode):
        return rdf.Iri(subject.value)
    raise TypeError(type(subject))


def _quad_subject_to_ox(subject: rdf.Quad_Subject) -> ox.BlankNode | ox.NamedNode:
    if isinstance(subject, rdf.BlankNode):
        return ox.BlankNode(subject)
    if isinstance(subject, rdf.Iri):
        return ox.NamedNode(subject)
    raise TypeError(type(subject))


def _quad_to_ox(quad: rdf.Quad) -> ox.Quad:
    return ox.Quad(
        _quad_subject_to_ox(quad[0]),
        _quad_predicate_to_ox(quad[1]),
        _quad_object_to_ox(quad[2]),
        _quad_graph_to_ox(quad[3]),
    )


class OxigraphStore(Store):
    """
    A store backed by Oxigraph, either in-memory or on disk.

    Adapted from oxrdflib.
    """

    @dataclass(frozen=True)
    class Descriptor(Store.Descriptor):
        directory_path: Path | None
        transactional: bool

    def __init__(
        self, *, directory_path: Maybe[Path], read_only: bool, transactional: bool
    ):
        self.__directory_path = directory_path.value_or(None)
        if self.__directory_path is not None:
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
        else:
            self.__delegate = ox.Store()
        self.__transactional = transactional

    def add(self, quad: rdf.Quad) -> None:
        self.__delegate.add(_quad_to_ox(quad))

    def close(self, commit_pending_transaction: bool = False) -> None:  # noqa: ARG002
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

    def _dump(self, *, format_: rdf.Format, output: IO[bytes]) -> None:
        self.__delegate.dump(
            format=pyoxigraph.RdfFormat.from_extension(format_.file_extension),
            output=output,
        )

    def extend(self, quads: Iterable[rdf.Quad]) -> None:
        if self.__transactional:
            self.__delegate.extend(_quad_to_ox(quad) for quad in quads)  # type: ignore
        else:
            self.__delegate.bulk_extend(_quad_to_ox(quad) for quad in quads)  # type: ignore

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
            _quad_subject_to_ox(subject) if subject is not None else None,
            _quad_predicate_to_ox(predicate) if predicate is not None else None,
            _quad_object_to_ox(object_) if object_ is not None else None,
            _quad_graph_to_ox(graph) if graph is not None else None,
        ):
            yield _quad_from_ox(quad)

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> Store:
        return OxigraphStore(
            directory_path=Maybe.from_optional(descriptor.directory_path),
            read_only=read_only,
            transactional=descriptor.transactional,
        )
