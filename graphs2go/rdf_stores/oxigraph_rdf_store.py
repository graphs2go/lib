from __future__ import annotations

import contextlib
from dataclasses import dataclass
from shutil import rmtree
from typing import TYPE_CHECKING, Any

import pyoxigraph
import pyoxigraph as ox
import rdflib.store
from rdflib.graph import (
    DATASET_DEFAULT_GRAPH_ID,
    Graph,
    _ContextType,
    _QuadType,
    _TriplePatternType,
    _TripleType,
)
from rdflib.term import BNode, Identifier, Literal, Node, URIRef

from graphs2go.rdf_stores.rdf_store import RdfStore

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator, Mapping
    from pathlib import Path

    from rdflib.plugins.sparql.sparql import Query, Update
    from rdflib.query import Result


_NONE_SINGLETON_TUPLE = (None,)


def _graph_from_ox(
    graph_name: ox.NamedNode | ox.BlankNode | ox.DefaultGraph, store: rdflib.store.Store
) -> Graph:
    if isinstance(graph_name, ox.DefaultGraph):
        return Graph(identifier=DATASET_DEFAULT_GRAPH_ID, store=store)
    if isinstance(graph_name, ox.NamedNode):
        return Graph(identifier=URIRef(graph_name.value), store=store)
    if isinstance(graph_name, ox.BlankNode):
        return Graph(identifier=BNode(graph_name.value), store=store)
    raise ValueError(f"unexpected Oxigraph graph name: {graph_name!r}")


def _graph_identifier_to_ox(
    graph_identifier: Node,
) -> ox.BlankNode | ox.DefaultGraph | ox.NamedNode:
    if graph_identifier == DATASET_DEFAULT_GRAPH_ID:
        return ox.DefaultGraph()
    if isinstance(graph_identifier, BNode):
        return ox.BlankNode(graph_identifier)
    if isinstance(graph_identifier, URIRef):
        return ox.NamedNode(graph_identifier)
    raise TypeError(graph_identifier)


def _literal_from_ox(literal: ox.Literal) -> Literal:
    if literal.language:
        return Literal(literal.value, lang=literal.language)
    return Literal(literal.value, datatype=URIRef(literal.datatype.value))


def _literal_to_ox(literal: Literal) -> ox.Literal:
    return ox.Literal(
        literal,
        language=literal.language,
        datatype=ox.NamedNode(literal.datatype) if literal.datatype else None,
    )


def _object_to_ox(
    object_: Node,
) -> ox.BlankNode | ox.Literal | ox.NamedNode:
    if isinstance(object_, BNode):
        return ox.BlankNode(object_)
    if isinstance(object_, Literal):
        return _literal_to_ox(object_)
    if isinstance(object_, URIRef):
        return ox.NamedNode(object_)
    raise TypeError(type(object_))


def _predicate_from_ox(predicate: ox.NamedNode) -> URIRef:
    return URIRef(predicate.value)


def _predicate_to_ox(predicate: Node) -> ox.NamedNode:
    assert isinstance(predicate, URIRef)
    return ox.NamedNode(predicate)


def _quad_to_ox(quad: _QuadType) -> ox.Quad:
    return ox.Quad(
        _subject_to_ox(quad[0]),
        _predicate_to_ox(quad[1]),
        _object_to_ox(quad[2]),
        _graph_identifier_to_ox(quad[3].identifier),
    )


def _quad_pattern_to_ox(
    triple: _TriplePatternType, context: Graph | None = None
) -> tuple[
    ox.BlankNode | ox.NamedNode | None,
    ox.NamedNode | None,
    ox.BlankNode | ox.Literal | ox.NamedNode | None,
    ox.BlankNode | ox.DefaultGraph | ox.NamedNode | None,
]:
    (s, p, o) = triple
    return (
        _subject_to_ox(s) if s is not None else None,
        _predicate_to_ox(p) if p is not None else None,
        _object_to_ox(o) if o is not None else None,
        _graph_identifier_to_ox(context.identifier) if context is not None else None,
    )


def _subject_from_ox(
    subject: ox.BlankNode | ox.NamedNode | ox.Triple,
) -> BNode | URIRef:
    if isinstance(subject, ox.BlankNode):
        return BNode(subject.value)
    if isinstance(subject, ox.NamedNode):
        return URIRef(subject.value)
    raise TypeError(type(subject))


def _subject_to_ox(subject: Node) -> ox.BlankNode | ox.NamedNode:
    if isinstance(subject, BNode):
        return ox.BlankNode(subject)
    if isinstance(subject, URIRef):
        return ox.NamedNode(subject)
    raise TypeError(type(subject))


def _triple_to_ox(triple: _TripleType, context: Graph) -> ox.Quad:
    return ox.Quad(
        _subject_to_ox(triple[0]),
        _predicate_to_ox(triple[1]),
        _object_to_ox(triple[2]),
        _graph_identifier_to_ox(context.identifier),
    )


def _object_from_ox(
    object_: ox.BlankNode | ox.Literal | ox.NamedNode | ox.Triple,
) -> BNode | Literal | URIRef:
    if isinstance(object_, ox.BlankNode):
        return BNode(object_.value)
    if isinstance(object_, ox.Literal):
        return _literal_from_ox(object_)
    if isinstance(object_, ox.NamedNode):
        return URIRef(object_.value)
    raise TypeError(type(object_))


class OxigraphRdfStore(RdfStore):
    """
    An Oxigraph-backed RdfStore/rdflib Store.

    Adapted from oxrdflib.
    """

    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        oxigraph_directory_path: Path
        transactional: bool

    context_aware: bool = True
    formula_aware: bool = False
    graph_aware: bool = True
    transaction_aware: bool = False

    def __init__(
        self, *, oxigraph_directory_path: Path, read_only: bool, transactional: bool
    ):
        super().__init__(configuration=None, identifier=None)
        self.__namespace_for_prefix: dict[str, URIRef] = {}
        self.__prefix_for_namespace: dict[URIRef, str] = {}
        self.__oxigraph_directory_path = oxigraph_directory_path
        if read_only:
            if not oxigraph_directory_path.is_dir():
                raise ValueError(
                    "store opened read-only but directory %s does not exist or is not a directory",
                    oxigraph_directory_path,
                )
            self.__delegate = ox.Store.read_only(str(oxigraph_directory_path))
        else:
            oxigraph_directory_path.mkdir(exist_ok=True, parents=True)
            self.__delegate = ox.Store(oxigraph_directory_path)
        self.__transactional = transactional

    def add(
        self,
        triple: _TripleType,
        context: Graph,
        quoted: bool = False,
    ) -> None:
        if quoted:
            raise ValueError("Oxigraph stores are not formula aware")
        self.__delegate.add(_triple_to_ox(triple, context))
        super().add(triple, context, quoted)

    def add_graph(self, graph: Graph) -> None:
        self.__delegate.add_graph(_graph_identifier_to_ox(graph.identifier))

    def addN(self, quads: Iterable[_QuadType]) -> None:  # noqa: N802
        if self.__transactional:
            self.__delegate.extend(_quad_to_ox(q) for q in quads)  # type: ignore
        else:
            self.__delegate.bulk_extend(_quad_to_ox(q) for q in quads)  # type: ignore

    def bind(
        self,
        prefix: str,
        namespace: URIRef,
        override: bool = True,
    ) -> None:
        if not override and (
            prefix in self.__namespace_for_prefix
            or namespace in self.__prefix_for_namespace
        ):
            return  # nothing to do
        self.__delete_from_prefix(prefix)
        self.__delete_from_namespace(namespace)
        self.__namespace_for_prefix[prefix] = namespace
        self.__prefix_for_namespace[namespace] = prefix

    def close(self, commit_pending_transaction: bool = False) -> None:  # noqa: ARG002
        # There's no explicit close on the pyoxigraph Store.
        # Delete all references to the pyoxigraph Store so it gets garbage collected and releases its lock.
        with contextlib.suppress(AttributeError):
            del self.__delegate

    def commit(self) -> None:
        # TODO: implement
        pass

    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[Graph, None, None]:
        if triple is None:
            return (_graph_from_ox(g, self) for g in self.__delegate.named_graphs())
        return (
            _graph_from_ox(q.graph_name, self)
            for q in self.__delegate.quads_for_pattern(*_quad_pattern_to_ox(triple))
        )

    def __delete_from_prefix(self, prefix: str) -> None:
        if prefix not in self.__namespace_for_prefix:
            return
        namespace = self.__namespace_for_prefix[prefix]
        del self.__namespace_for_prefix[prefix]
        self.__delete_from_namespace(namespace)

    def __delete_from_namespace(self, namespace: URIRef) -> None:
        if namespace not in self.__prefix_for_namespace:
            return
        prefix = self.__prefix_for_namespace[namespace]
        del self.__prefix_for_namespace[namespace]
        self.__delete_from_prefix(prefix)

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            oxigraph_directory_path=self.__oxigraph_directory_path,
            transactional=self.__transactional,
        )

    def destroy(self, configuration: str) -> None:  # noqa: ARG002
        rmtree(self.__oxigraph_directory_path)

    def gc(self) -> None:
        pass

    @property
    def is_empty(self) -> bool:
        for _ in self.triples((None, None, None)):
            return False
        return True

    def __len__(self, context: _ContextType | None = None) -> int:
        raise NotImplementedError

    def load(self, *, mime_type: str, source: Path) -> None:
        with source.open("rb") as input_:
            if self.__transactional:
                self.pyoxigraph_store.load(
                    input=input_, format=pyoxigraph.RdfFormat.from_media_type(mime_type)
                )
            else:
                self.pyoxigraph_store.bulk_load(
                    input=input_, format=pyoxigraph.RdfFormat.from_media_type(mime_type)
                )

    def namespace(self, prefix: str) -> URIRef | None:
        return self.__namespace_for_prefix.get(prefix)

    def namespaces(self) -> Iterator[tuple[str, URIRef]]:
        yield from self.__namespace_for_prefix.items()

    def open(
        self,
        configuration: str,  # noqa: ARG002
        create: bool = False,  # noqa: ARG002
    ) -> int | None:
        return rdflib.store.VALID_STORE

    def prefix(self, namespace: URIRef) -> str | None:
        return self.__prefix_for_namespace.get(namespace)

    @property
    def pyoxigraph_store(self) -> ox.Store:
        return self.__delegate

    def query(
        self,
        query: Query | str,
        initNs: Mapping[str, Any],  # noqa: N803
        initBindings: Mapping[str, Identifier],  # noqa: N803
        queryGraph: str,  # noqa: N803
        **kwargs: Any,
    ) -> Result:
        raise NotImplementedError("adapt from oxrdflib if needed")

    def remove(
        self,
        triple: _TriplePatternType,
        context: Graph | None = None,
    ) -> None:
        for q in self.__delegate.quads_for_pattern(
            *_quad_pattern_to_ox(triple, context)
        ):
            self.__delegate.remove(q)
        super().remove(triple, context)

    def remove_graph(self, graph: Graph) -> None:
        self.__delegate.remove_graph(_graph_identifier_to_ox(graph.identifier))

    def rollback(self) -> None:
        # TODO: implement
        pass

    def triples(
        self,
        triple_pattern: _TriplePatternType,
        context: Graph | None = None,
    ) -> Iterator[tuple[_TripleType, Iterator[Graph | None]]]:
        for quad in self.__delegate.quads_for_pattern(
            *_quad_pattern_to_ox(triple_pattern, context)
        ):
            graphs: tuple[Graph | None, ...]
            if quad.graph_name == ox.DefaultGraph():
                graphs = _NONE_SINGLETON_TUPLE
            else:
                graphs = (_graph_from_ox(quad.graph_name, store=self),)

            yield (
                (
                    _subject_from_ox(quad.subject),
                    _predicate_from_ox(quad.predicate),
                    _object_from_ox(quad.object),
                ),
                iter(graphs),
            )

    def update(
        self,
        update: Update | str,
        initNs: Mapping[str, Any],  # noqa: N803
        initBindings: Mapping[str, Identifier],  # noqa: N803
        queryGraph: str,  # noqa: N803
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError
