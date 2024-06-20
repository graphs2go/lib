from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import rdflib.store
from pathvalidate import sanitize_filename
from rdflib import ConjunctiveGraph
from returns.maybe import Some
from returns.pipeline import is_successful

if TYPE_CHECKING:
    from pathlib import Path

    from rdflib import URIRef

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class RdfStore(rdflib.store.Store, ABC):
    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @staticmethod
    def create_(*, identifier: URIRef, rdf_store_config: RdfStoreConfig) -> RdfStore:
        rdf_store_config_parsed = rdf_store_config.parse()

        if not is_successful(rdf_store_config_parsed.directory_path):
            from .memory_rdf_store import MemoryRdfStore

            return MemoryRdfStore()

        from .oxigraph_rdf_store import OxigraphRdfStore

        oxigraph_subdirectory_path = (
            rdf_store_config_parsed.directory_path.unwrap()
            / sanitize_filename(identifier)
        )
        oxigraph_subdirectory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphRdfStore(
            oxigraph_directory_path=oxigraph_subdirectory_path,
            read_only=False,
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
    def open_(descriptor: Descriptor, *, read_only: bool = False) -> RdfStore:
        from .memory_rdf_store import MemoryRdfStore
        from .oxigraph_rdf_store import OxigraphRdfStore

        if isinstance(descriptor, MemoryRdfStore.Descriptor):
            return MemoryRdfStore(memory=Some(descriptor.memory))
        if isinstance(descriptor, OxigraphRdfStore.Descriptor):
            descriptor_: OxigraphRdfStore.Descriptor = descriptor
            return OxigraphRdfStore(
                oxigraph_directory_path=descriptor_.oxigraph_directory_path,
                read_only=read_only,
                transactional=descriptor_.transactional,
            )
        raise TypeError(type(descriptor))
