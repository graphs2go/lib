from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Iterator, Tuple

import oxrdflib
import pyoxigraph
import pyoxigraph as ox
from pathvalidate import sanitize_filename
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID, Graph
from rdflib.term import BNode, Literal, URIRef

from graphs2go.rdf_stores.rdf_store import RdfStore

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    import rdflib.store
    from rdflib.graph import _QuadType


def _literal_to_ox(literal: Literal) -> ox.Literal:
    return ox.Literal(
        literal,
        language=literal.language,
        datatype=ox.NamedNode(literal.datatype) if literal.datatype else None,
    )


def _quad_to_ox(quad: _QuadType) -> ox.Quad:
    s, p, o, c = quad

    s_ox: ox.BlankNode | ox.NamedNode
    if isinstance(s, BNode):
        s_ox = ox.BlankNode(s)
    elif isinstance(s, URIRef):
        s_ox = ox.NamedNode(s)
    else:
        raise TypeError(type(s))

    assert isinstance(p, URIRef)
    p_ox = ox.NamedNode(p)

    o_ox: ox.BlankNode | ox.Literal | ox.NamedNode
    if isinstance(o, BNode):
        o_ox = ox.BlankNode(o)
    elif isinstance(o, Literal):
        o_ox = _literal_to_ox(o)
    elif isinstance(o, URIRef):
        o_ox = ox.NamedNode(o)
    else:
        raise TypeError(type(o))

    c_ox: None | ox.DefaultGraph | ox.NamedNode
    if c is None:
        c_ox = None
    elif c == DATASET_DEFAULT_GRAPH_ID:
        c_ox = ox.DefaultGraph()
    elif isinstance(c, Graph):
        if isinstance(c.identifier, BNode):
            c_ox = ox.DefaultGraph()
            # c_ox = ox.BlankNode(c.identifier)
        elif isinstance(c.identifier, URIRef):
            c_ox = ox.NamedNode(c.identifier)
        else:
            raise TypeError(c.identifier)
    else:
        raise TypeError(type(c))

    return ox.Quad(s_ox, p_ox, o_ox, c_ox)


class _OxigraphRdflibStore(oxrdflib.OxigraphStore):
    def triples(
        self,
        triple_pattern: _TriplePattern,
        context: Optional[Graph] = None,
    ) -> Iterator[Tuple[_Triple, Iterator[Optional[Graph]]]]:
        for ox_quad in self._inner.quads_for_pattern(
            *_to_ox_quad_pattern(triple_pattern, context)
        ):
            pass

        # return (
        #     (
        #         (_from_ox(q.subject), _from_ox(q.predicate), _from_ox(q.object)),
        #         iter(
        #             (
        #                 (
        #                     _from_ox_graph_name(q.graph_name, self)
        #                     if q.graph_name != ox.DefaultGraph()
        #                     else None
        #                 ),
        #             )
        #         ),
        #     )
        #     for q in
        # )


class OxigraphRdfStore(RdfStore):
    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        oxigraph_directory_path: Path
        transactional: bool

    def __init__(
        self, *, oxigraph_directory_path: Path, read_only: bool, transactional: bool
    ):
        self.__oxigraph_directory_path = oxigraph_directory_path
        self.__pyoxigraph_store = (
            pyoxigraph.Store.secondary(str(oxigraph_directory_path))
            if read_only
            else pyoxigraph.Store(oxigraph_directory_path)
        )
        self.__rdflib_store = oxrdflib.OxigraphStore(store=self.__pyoxigraph_store)
        self.__transactional = transactional

    def add_all(self, quads: Iterable[_QuadType]) -> None:
        if self.__transactional:
            self.__pyoxigraph_store.extend(_quad_to_ox(q) for q in quads)  # type: ignore
        else:
            self.__pyoxigraph_store.bulk_extend(_quad_to_ox(q) for q in quads)  # type: ignore

    def load(self, *, mime_type: str, source: Path) -> None:
        if self.__transactional:
            self.pyoxigraph_store.load(input=source, mime_type=mime_type)
        else:
            self.pyoxigraph_store.bulk_load(input=source, mime_type=mime_type)

    def close(self) -> None:
        # There's no explicit close on the pyoxigraph Store.
        # Delete all references to the pyoxigraph Store so it gets garbage collected and releases its lock.
        try:
            del self.__pyoxigraph_store
            del self.__rdflib_store
        except AttributeError:
            pass

    @staticmethod
    def create(  # type: ignore
        *, identifier: URIRef, oxigraph_directory_path: Path, transactional: bool
    ) -> OxigraphRdfStore:
        oxigraph_subdirectory_path = oxigraph_directory_path / sanitize_filename(
            identifier
        )
        oxigraph_subdirectory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphRdfStore(
            oxigraph_directory_path=oxigraph_subdirectory_path,
            read_only=False,
            transactional=transactional,
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            oxigraph_directory_path=self.__oxigraph_directory_path,
            transactional=self.__transactional,
        )

    @staticmethod
    def open(  # type: ignore
        descriptor: RdfStore.Descriptor, *, read_only: bool = False
    ) -> OxigraphRdfStore:
        assert isinstance(descriptor, OxigraphRdfStore.Descriptor)
        return OxigraphRdfStore(
            oxigraph_directory_path=descriptor.oxigraph_directory_path,
            read_only=read_only,
            transactional=descriptor.transactional,
        )

    @property
    def rdflib_store(self) -> rdflib.store.Store:
        return self.__rdflib_store

    @property
    def pyoxigraph_store(self) -> pyoxigraph.Store:
        return self.__pyoxigraph_store
