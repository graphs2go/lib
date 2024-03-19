from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import rdflib

from graphs2go.rdf_stores.rdf_store import RdfStore

if TYPE_CHECKING:
    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class PersistentRdfGraph:
    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying a graph.
        """

        rdf_store_descriptor: RdfStore.Descriptor

    def __init__(self, *, rdf_store: RdfStore):
        self._rdflib_graph = rdflib.ConjunctiveGraph(store=rdf_store.rdflib_store)
        self.__rdf_store = rdf_store

    @classmethod
    def create(
        cls,
        *,
        identifier: rdflib.URIRef,
        rdf_store_config: RdfStoreConfig,
    ) -> Self:
        return cls(
            rdf_store=RdfStore.create(
                identifier=identifier, rdf_store_config=rdf_store_config
            )
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(rdf_store_descriptor=self.__rdf_store.descriptor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self._rdflib_graph.close()

    @property
    def is_empty(self) -> bool:
        return self.__rdf_store.is_empty

    @classmethod
    def open(cls, descriptor: Descriptor) -> Self:
        return cls(rdf_store=RdfStore.open(descriptor.rdf_store_descriptor))
