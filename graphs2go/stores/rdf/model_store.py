from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from graphs2go.models import rdf
from graphs2go.models.rdf import ResourceSet
from graphs2go.namespaces import RDF
from graphs2go.stores.rdf.quad_store import QuadStore
from graphs2go.stores.store import Store

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


def _model_to_quads(model: rdf.Model) -> Iterable[rdf.Quad]:
    yield from model.resource.dataset.match()


class ModelStore[ModelT: rdf.Model](Store):
    """
    Non-picklable RDF model store backed by an RDF quad store.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF model store.
        """

        quad_store_descriptor: QuadStore.Descriptor

        @property
        def identifier(self) -> Store.Identifier:
            return self.quad_store_descriptor.identifier

    def __init__(self, *, quad_store: QuadStore):
        self._quad_store = quad_store
        self._resource_set = ResourceSet(dataset=quad_store)

    def add(self, model: ModelT) -> Self:
        self._quad_store.extend(_model_to_quads(model))
        return self

    def close(self) -> None:
        self._quad_store.close()

    @classmethod
    def create(cls, *, config: RdfStoreConfig, identifier: Store.Identifier) -> Self:
        return cls(
            quad_store=QuadStore.create(config=config, identifier=identifier),
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            quad_store_descriptor=self._quad_store.descriptor,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    def extend(self, models: Iterable[ModelT]) -> Self:
        def models_to_quads() -> Iterable[rdf.Quad]:
            for model in models:
                yield from _model_to_quads(model)

        self._quad_store.extend(models_to_quads())
        return self

    def extend_if_empty(self, lazy_models: Callable[[], Iterable[ModelT]]) -> Self:
        if self.is_empty:
            self.extend(lazy_models())
        return self

    @property
    def identifier(self) -> Store.Identifier:
        return self._quad_store.identifier

    @property
    def is_empty(self) -> bool:
        return self._quad_store.is_empty

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> Self:
        return cls(
            quad_store=QuadStore.open(
                descriptor.quad_store_descriptor, read_only=read_only
            ),
        )

    def _models_by_rdf_type[NarrowerModelT: rdf.Model](
        self, *, model_class: type[NarrowerModelT], rdf_type: rdf.Iri
    ) -> Iterable[NarrowerModelT]:
        return (
            model_class(self._resource_set.named_resource(model_iri))
            for model_iri in self._model_iris_by_rdf_type(rdf_type)
        )

    def _model_iris_by_rdf_type(self, rdf_type: rdf.Iri) -> Iterable[rdf.Iri]:
        return (
            quad.subject
            for quad in self._quad_store.match(predicate=RDF.type, object_=rdf_type)
            if isinstance(quad.subject, rdf.Iri)
        )

    @property
    def quad_store(self) -> QuadStore:
        return self._quad_store
