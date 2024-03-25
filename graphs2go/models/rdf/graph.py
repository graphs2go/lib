from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, TypeVar

import rdflib

from graphs2go.models.rdf.model import Model
from graphs2go.rdf_stores.rdf_store import RdfStore

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rdflib.graph import _QuadType

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


_ModelT = TypeVar("_ModelT", bound=Model)


def _rdflib_graph_to_quads(rdflib_graph: rdflib.Graph) -> Iterable[_QuadType]:
    for s, p, o in rdflib_graph:
        yield s, p, o, rdflib_graph


class Graph:
    """
    Non-picklable RDF graph backed by RDF store.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF graph.
        """

        identifier: rdflib.URIRef
        rdf_store_descriptor: RdfStore.Descriptor

    def __init__(self, *, identifier: rdflib.URIRef, rdf_store: RdfStore):
        self.__identifier = identifier
        self.__rdflib_graph = rdflib.ConjunctiveGraph(
            identifier=identifier, store=rdf_store
        )
        self.__rdf_store = rdf_store

    def _add(self, model: Model) -> None:
        self.__rdf_store.addN(_rdflib_graph_to_quads(model.resource.graph))

    def _add_all(self, models: Iterable[Model]) -> None:
        def models_to_quads() -> Iterable[_QuadType]:
            for model in models:
                yield from _rdflib_graph_to_quads(model.resource.graph)

        self.__rdf_store.addN(models_to_quads())

    @classmethod
    def create(
        cls, *, identifier: rdflib.URIRef, rdf_store_config: RdfStoreConfig
    ) -> Self:
        return cls(
            identifier=identifier,
            rdf_store=RdfStore.create_(
                identifier=identifier, rdf_store_config=rdf_store_config
            ),
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            identifier=self.__identifier,
            rdf_store_descriptor=self.__rdf_store.descriptor,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.__rdflib_graph.close()
        self.__rdf_store.close()

    @property
    def identifier(self) -> rdflib.URIRef:
        return self.__identifier

    @property
    def is_empty(self) -> bool:
        return self.__rdf_store.is_empty

    def _models_by_rdf_type(
        self, model_class: type[_ModelT], *, rdf_type: rdflib.URIRef | None = None
    ) -> Iterable[_ModelT]:
        if rdf_type is None:
            rdf_type = model_class.primary_rdf_type()

        yielded_model_uris: set[rdflib.URIRef] = set()
        for model_uri in self.__rdflib_graph.subjects(
            predicate=rdflib.RDF.type,
            object=rdf_type,
            unique=True,
        ):
            if not isinstance(model_uri, rdflib.URIRef):
                continue
            if model_uri in yielded_model_uris:
                continue

            yield model_class(resource=self.__rdflib_graph.resource(model_uri))
            yielded_model_uris.add(model_uri)

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> Self:
        return cls(
            identifier=descriptor.identifier,
            rdf_store=RdfStore.open_(
                descriptor.rdf_store_descriptor, read_only=read_only
            ),
        )

    @property
    def rdflib_graph(self) -> rdflib.Graph:
        return self.__rdflib_graph
