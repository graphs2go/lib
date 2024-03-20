from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from rdflib import ConjunctiveGraph

from graphs2go.rdf_stores.memory_rdf_store import MemRdfStore

if TYPE_CHECKING:
    from pathlib import Path
    from rdflib import URIRef
    from rdflib.store import Store

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class RdfStore(ABC):
    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

    def bulk_load(self, *, mime_type: str, source: Path) -> None:
        """
        Bulk load the contents of the input into the store.

        No transactional guarantee.
        """

        ConjunctiveGraph(store=self.rdflib_store).parse(
            format=mime_type,
            source=source,
        )

    @abstractmethod
    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @staticmethod
    def create(
        *,
        identifier: URIRef,
        rdf_store_config: RdfStoreConfig,
    ) -> RdfStore:
        from .oxigraph_rdf_store import OxigraphRdfStore

        return OxigraphRdfStore.create(
            identifier=identifier,
            rdf_store_config=rdf_store_config,
        )

    @property
    @abstractmethod
    def descriptor(self) -> Descriptor:
        pass

    @property
    def is_empty(self) -> bool:
        for _ in self.rdflib_store.triples((None, None, None)):
            return False
        return True

    @staticmethod
    def open(descriptor: Descriptor) -> RdfStore:
        from .memory_rdf_store import MemoryRdfStore
        from .oxigraph_rdf_store import OxigraphRdfStore

        if isinstance(descriptor, MemoryRdfStore.Descriptor):
            return MemoryRdfStore()
        if isinstance(descriptor, OxigraphRdfStore.Descriptor):
            return OxigraphRdfStore.open(descriptor)
        raise TypeError(type(descriptor))

    @property
    @abstractmethod
    def rdflib_store(self) -> Store:
        pass
