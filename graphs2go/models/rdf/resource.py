from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime
from decimal import Decimal
from typing import Self, TypeVar

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.term import Node
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import is_successful

_ValueT = TypeVar("_ValueT")
_ValueMapper = Callable[[Node, Node, Node, Graph], Maybe[_ValueT]]


class Resource:
    """
    Bespoke RDF Resource class, in lieu of the rdflib Resource.
    """

    Identifier = BNode | URIRef

    class Builder:
        def __init__(self, *, graph: Graph, identifier: Resource.Identifier) -> None:
            self.__graph = graph
            self.__identifier = identifier

        def add(self, predicate: URIRef, object_: Node) -> Self:
            self.__graph.add((self.__identifier, predicate, object_))
            return self

        def build(self) -> Resource:
            return Resource(graph=self.__graph, identifier=self.__identifier)

        @property
        def graph(self) -> Graph:
            return self.__graph

        @property
        def identifier(self) -> BNode | URIRef:
            return self.__identifier

        def set(self, predicate: URIRef, object_: Node) -> Self:
            self.__graph.set((self.__identifier, predicate, object_))
            return self

    class ValueMappers:
        @staticmethod
        def bool(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[bool]:
            if not isinstance(object_, Literal):
                return Nothing
            value_py = object_.toPython()
            return Some(value_py) if isinstance(value_py, bool) else Nothing

        @staticmethod
        def datetime(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[datetime]:
            if not isinstance(object_, Literal):
                return Nothing
            value_py = object_.toPython()
            return Some(value_py) if isinstance(value_py, datetime) else Nothing

        @staticmethod
        def identifier(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[Resource.Identifier]:
            return Some(object_) if isinstance(object_, BNode | URIRef) else Nothing

        @staticmethod
        def identity(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[Node]:
            return Some(object_)

        @staticmethod
        def int(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[int]:
            if not isinstance(object_, Literal):
                return Nothing
            value_py = object_.toPython()
            if isinstance(value_py, Decimal | float | int):
                return Some(int(value_py))
            return Nothing

        @staticmethod
        def iri(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[URIRef]:
            return Some(object_) if isinstance(object_, URIRef) else Nothing

        @staticmethod
        def literal(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[Literal]:
            return Some(object_) if isinstance(object_, Literal) else Nothing

        @staticmethod
        def named_resource(
            subject: Node, predicate: Node, object_: Node, graph: Graph
        ) -> Maybe[Resource]:
            from .named_resource import NamedResource

            return Resource.ValueMappers.iri(subject, predicate, object_, graph).map(
                lambda iri: NamedResource(graph=graph, iri=iri)
            )

        @staticmethod
        def resource(
            subject: Node, predicate: Node, object_: Node, graph: Graph
        ) -> Maybe[Resource]:
            return Resource.ValueMappers.identifier(
                subject, predicate, object_, graph
            ).map(lambda identifier: Resource(graph=graph, identifier=identifier))

        @staticmethod
        def str(
            _subject: Node, _predicate: Node, object_: Node, _graph: Graph
        ) -> Maybe[str]:
            if not isinstance(object_, Literal):
                return Nothing
            value_py = object_.toPython()
            return Some(value_py) if isinstance(value_py, str) else Nothing

    def __init__(self, *, graph: Graph, identifier: BNode | URIRef):
        self.__graph = graph
        self.__identifier = identifier

    @classmethod
    def builder(cls, *, graph: Graph, identifier: Identifier) -> Builder:
        return cls.Builder(graph=graph, identifier=identifier)

    @property
    def graph(self) -> Graph:
        return self.__graph

    def has_value(
        self, predicate: URIRef, mapper: _ValueMapper = ValueMappers.identity
    ) -> bool:
        for _value in self.values(predicate, mapper=mapper):  # type: ignore
            return True
        return False

    @property
    def identifier(self) -> Identifier:
        return self.__identifier

    def optional_value(
        self, predicate: URIRef, mapper: _ValueMapper = ValueMappers.identity
    ) -> Maybe[_ValueT]:  # type: ignore
        for value in self.values(predicate, mapper=mapper):  # type: ignore
            return Some(value)
        return Nothing

    def optional_value_with_default(
        self,
        predicate: URIRef,
        default: _ValueT,
        mapper: _ValueMapper = ValueMappers.identity,
    ) -> _ValueT:  # type: ignore
        for value in self.values(predicate, mapper=mapper):  # type: ignore
            return value
        return default

    def required_value(
        self, predicate: URIRef, mapper: _ValueMapper = ValueMappers.identity
    ) -> _ValueT:  # type: ignore
        value: Maybe[_ValueT] = self.optional_value(predicate, mapper=mapper)
        if not is_successful(value):
            raise KeyError("missing required value for " + str(predicate))
        return value.unwrap()

    def values(
        self,
        predicate: URIRef,
        mapper: _ValueMapper = ValueMappers.identity,
    ) -> Iterable[_ValueT]:  # type: ignore
        for value in self.__graph.objects(subject=self.identifier, predicate=predicate):
            mapped_value = mapper(self.identifier, predicate, value, self.__graph)
            if is_successful(mapped_value):
                yield mapped_value.unwrap()
