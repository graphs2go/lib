from __future__ import annotations
from dataclasses import dataclass
import rdflib

from graphs2go.rdf_stores.rdf_store import RdfStore
from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphs2go.resources.rdf_store_config import RdfStoreConfig
    from graphs2go.models.interchange.model import Model
    from collections.abc import Iterable


class Graph:
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an interchange graph.
        """

        rdf_store_descriptor: RdfStore.Descriptor

    def __init__(self, *, rdf_store: RdfStore):
        self.__rdf_graph = rdflib.ConjunctiveGraph(store=rdf_store.rdflib_store)
        self.__rdf_store = rdf_store

    def add(self, model: Model) -> None:
        self.__rdf_graph += model.resource.graph

    @staticmethod
    def create(
        *,
        identifier: rdflib.URIRef,
        rdf_store_config: RdfStoreConfig,
    ) -> Graph:
        return Graph(
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
        self.__rdf_graph.close()

    @property
    def is_empty(self) -> bool:
        return self.__rdf_store.is_empty

    @property
    def nodes(self) -> Iterable[Node]:
        for subject_uri in self.__rdf_graph.subjects(
            predicate=rdflib.RDF.type, object=INTERCHANGE.Node
        ):
            yield Node(resource=self.__rdf_graph.resource(subject_uri))

    @staticmethod
    def open(descriptor: Descriptor) -> Graph:
        return Graph(rdf_store=RdfStore.open(descriptor.rdf_store_descriptor))
