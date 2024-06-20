from collections.abc import Generator, Iterator
from dataclasses import dataclass

from rdflib import URIRef
from rdflib.graph import Graph, _ContextType, _TriplePatternType, _TripleType
from rdflib.plugins.stores.memory import Memory
from returns.maybe import Maybe, Nothing

from graphs2go.rdf_stores.rdf_store import RdfStore


class MemoryRdfStore(RdfStore):
    context_aware = True
    formula_aware = True
    graph_aware = True

    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        memory: Memory

    def __init__(self, *, memory: Maybe[Memory] = Nothing):
        RdfStore.__init__(self)
        self.__memory = memory.or_else_call(lambda: Memory())
        self.__descriptor = self.Descriptor(self.__memory)

    def add(
        self,
        triple: _TripleType,
        context: _ContextType,
        quoted: bool = False,
    ) -> None:
        self.__memory.add(triple, context, quoted)

    def add_graph(self, graph: Graph) -> None:
        self.__memory.add_graph(graph)

    def bind(
        self,
        prefix: str,
        namespace: URIRef,
        override: bool = True,
    ) -> None:
        self.__memory.bind(prefix, namespace, override)

    def contexts(
        self, triple: _TripleType | None = None
    ) -> Generator[_ContextType, None, None]:
        yield from self.__memory.contexts(triple)

    @property
    def descriptor(self) -> Descriptor:
        return self.__descriptor

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    def __len__(self, context: _ContextType | None = None) -> int:
        return len(self.__memory)

    def namespace(self, prefix: str) -> URIRef | None:
        return self.__memory.namespace(prefix)

    def namespaces(self) -> Iterator[tuple[str, URIRef]]:
        return self.__memory.namespaces()

    def prefix(self, namespace: URIRef) -> str | None:
        return self.__memory.prefix(namespace)

    def remove(
        self,
        triple_pattern: _TriplePatternType,
        context: _ContextType | None = None,
    ) -> None:
        self.__memory.remove(triple_pattern, context)

    def remove_graph(self, graph: Graph) -> None:
        self.__memory.remove_graph(graph)

    def triples(
        self,
        triple_pattern: _TriplePatternType,
        context: _ContextType | None = None,
    ) -> Generator[
        tuple[_TripleType, Generator[_ContextType | None, None, None]],
        None,
        None,
    ]:
        yield from self.__memory.triples(triple_pattern, context)
