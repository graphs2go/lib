from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, TypeVar

import rdflib

from graphs2go.models.rdf.model import Model
from graphs2go.rdf_stores.rdf_store import RdfStore

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


_ModelT = TypeVar("_ModelT", bound=Model)


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
        self._rdflib_graph = rdflib.ConjunctiveGraph(
            identifier=identifier, store=rdf_store.rdflib_store
        )
        self.__rdf_store = rdf_store

    @classmethod
    def create(
        cls,
        *,
        identifier: rdflib.URIRef,
        rdf_store_config: RdfStoreConfig,
    ) -> Self:
        return cls(
            identifier=identifier,
            rdf_store=RdfStore.create(
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
        self._rdflib_graph.close()

    @property
    def identifier(self) -> rdflib.URIRef:
        return self.__identifier

    @property
    def is_empty(self) -> bool:
        return self.__rdf_store.is_empty

    def _models_by_rdf_type(
        self, model_classes: type[_ModelT] | tuple[type[_ModelT], ...]
    ) -> Iterable[_ModelT]:
        """
        Generate models from the graph according to their rdf:type's.

        A given model resource (subject URI) will only produce a single Model instance.
        Resources with multiple rdf:type statements will match the first rdf:type in the model_classes tuple.
        This means that "subclasses" can be included earlier in the tuple in order to wrap the resource in the
        subclass rather than the parent class.
        """

        if not isinstance(model_classes, tuple):
            model_classes = (model_classes,)

        yielded_model_uris: set[rdflib.URIRef] = set()
        for model_class in model_classes:
            for model_uri in self._rdflib_graph.subjects(
                predicate=rdflib.RDF.type,
                object=model_class.rdf_type_uri(),
                unique=True,
            ):
                if not isinstance(model_uri, rdflib.URIRef):
                    continue
                if model_uri in yielded_model_uris:
                    continue

                yield model_class(resource=self._rdflib_graph.resource(model_uri))
                yielded_model_uris.add(model_uri)

    @classmethod
    def open(cls, descriptor: Descriptor) -> Self:
        return cls(
            identifier=descriptor.identifier,
            rdf_store=RdfStore.open(descriptor.rdf_store_descriptor),
        )

    def to_rdflib_graph(self) -> rdflib.Graph:
        return self._rdflib_graph
