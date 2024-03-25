from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from rdflib import ConjunctiveGraph
import rdflib.store

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from rdflib import URIRef
    from rdflib.graph import _QuadType

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class RdfStore(rdflib.store.Store, ABC):
    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

    @abstractmethod
    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @staticmethod
    def create(*, identifier: URIRef, rdf_store_config: RdfStoreConfig) -> RdfStore:
        rdf_store_config_parsed = rdf_store_config.parse()

        from .oxigraph_rdf_store import OxigraphRdfStore

        return OxigraphRdfStore.create(
            identifier=identifier,
            oxigraph_directory_path=rdf_store_config_parsed.directory_path,
            transactional=rdf_store_config_parsed.transactional,
        )

    @property
    @abstractmethod
    def descriptor(self) -> Descriptor:
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        pass

    def load(self, *, mime_type: str, source: Path) -> None:
        ConjunctiveGraph(store=self).parse(
            format=mime_type,
            source=source,
        )

    @staticmethod
    def open(descriptor: Descriptor, *, read_only: bool = False) -> RdfStore:
        from .memory_rdf_store import MemoryRdfStore
        from .oxigraph_rdf_store import OxigraphRdfStore

        if isinstance(descriptor, MemoryRdfStore.Descriptor):
            return MemoryRdfStore()
        if isinstance(descriptor, OxigraphRdfStore.Descriptor):
            return OxigraphRdfStore.open(descriptor, read_only=read_only)
        raise TypeError(type(descriptor))
