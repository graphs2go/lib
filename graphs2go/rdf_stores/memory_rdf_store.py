from collections.abc import Generator
from dataclasses import dataclass
from typing import Optional, Iterator

from rdflib.plugins.stores.memory import Memory

from graphs2go.rdf_stores.rdf_store import RdfStore


class MemoryRdfStore(RdfStore):
    context_aware = True
    formula_aware = True
    graph_aware = True

    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        pass

    __descriptor = Descriptor()

    def __init__(self):
        RdfStore.__init__(self)
        self.__delegate = Memory()

    def add(
        self,
        triple: "_TripleType",
        context: "_ContextType",
        quoted: bool = False,
    ) -> None:
        self.__delegate.add(triple, context, quoted)

    def add_graph(self, graph: "Graph") -> None:
        self.__delegate.add_graph(graph)

    def bind(self, prefix: str, namespace: "URIRef", override: bool = True) -> None:
        self.__delegate.bind(prefix, namespace, override)

    def close(self) -> None:
        pass

    def contexts(
        self, triple: Optional["_TripleType"] = None
    ) -> Generator["_ContextType", None, None]:
        yield from self.__delegate.contexts(triple)

    @property
    def descriptor(self) -> Descriptor:
        return self.__descriptor

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    def __len__(self, context: Optional["_ContextType"] = None) -> int:
        return len(self.__delegate)

    def namespace(self, prefix: str) -> Optional["URIRef"]:
        return self.__delegate.namespace(prefix)

    def namespaces(self) -> Iterator[tuple[str, "URIRef"]]:
        return self.__delegate.namespaces()

    def prefix(self, namespace: "URIRef") -> Optional[str]:
        return self.__delegate.prefix(namespace)

    def remove(
        self,
        triple_pattern: "_TriplePatternType",
        context: Optional["_ContextType"] = None,
    ) -> None:
        self.__delegate.remove(triple_pattern, context)

    def remove_graph(self, graph: "Graph") -> None:
        self.__delegate.remove_graph(graph)

    def triples(
        self,
        triple_pattern: "_TriplePatternType",
        context: Optional["_ContextType"] = None,
    ) -> Generator[
        tuple["_TripleType", Generator[Optional["_ContextType"], None, None]],
        None,
        None,
    ]:
        yield from self.__delegate.triples(triple_pattern, context)
