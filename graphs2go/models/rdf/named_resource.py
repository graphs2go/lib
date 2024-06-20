from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import Graph
from returns.maybe import Maybe, Nothing

from graphs2go.models.rdf.resource import Resource

if TYPE_CHECKING:
    from rdflib import URIRef


class NamedResource(Resource):
    class Builder(Resource.Builder):
        def __init__(self, *, graph: Graph, iri: URIRef):
            Resource.Builder.__init__(self, graph=graph, identifier=iri)
            self.__iri = iri

        def build(self) -> NamedResource:
            return NamedResource(graph=self.__graph, iri=self.__iri)

        @property
        def iri(self) -> URIRef:
            return self.__iri

    def __init__(self, *, graph: Graph, iri: URIRef):
        Resource.__init__(self, graph=graph, identifier=iri)
        self.__iri = iri

    @classmethod
    def builder(cls, *, iri: URIRef, graph: Maybe[Graph] = Nothing) -> Builder:  # type: ignore
        return cls.Builder(graph=graph.or_else_call(lambda: Graph()), iri=iri)

    @property
    def iri(self) -> URIRef:
        return self.__iri
