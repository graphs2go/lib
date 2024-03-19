from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from graphs2go.resources.rdf_store_config import RdfStoreConfig
    from rdflib.store import Store
    from rdflib import URIRef


class RdfStore(ABC):
    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

    @staticmethod
    def create(
        *,
        identifier: URIRef,
        rdf_store_config: RdfStoreConfig,
    ) -> RdfStore:
        from .oxigraph_rdf_store import OxigraphRdfStore

        return OxigraphRdfStore.create(
            identifier=identifier,
            rdf_store_config_parsed=rdf_store_config.parse(),
        )

    @property
    @abstractmethod
    def descriptor(self) -> Descriptor:
        pass

    @staticmethod
    def open(descriptor: Descriptor) -> RdfStore:
        from .oxigraph_rdf_store import OxigraphRdfStore

        if isinstance(descriptor, OxigraphRdfStore.Descriptor):
            return OxigraphRdfStore.open(descriptor)
        raise TypeError(type(descriptor))

    @abstractmethod
    def to_rdflib_store(self) -> Store:
        pass
