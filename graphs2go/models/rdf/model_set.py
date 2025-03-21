from collections.abc import Iterable, Callable
from typing import Self, TypeVar

from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.quad import Quad
from graphs2go.models.rdf.model import Model
from graphs2go.models.rdf.dataset import Dataset
from graphs2go.models.rdf.resource_set import ResourceSet
from graphs2go.namespaces import RDF


ModelT = TypeVar("ModelT", bound=Model)


def _model_to_quads(model: Model) -> Iterable[Quad]:
    yield from model.resource.dataset.match()


class ModelSet[ModelT]:
    def __init__(self, *, dataset: Dataset):
        self._dataset = dataset
        self._resource_set = ResourceSet(dataset=dataset)

    def add(self, model: ModelT) -> Self:
        self._dataset.extend(_model_to_quads(model))
        return self

    def add_all_if_empty(self, lazy_models: Callable[[], Iterable[ModelT]]) -> Self:
        if self.is_empty:
            self.extend(lazy_models())
        return self

    def extend(self, models: Iterable[ModelT]) -> Self:
        def models_to_quads() -> Iterable[Quad]:
            for model in models:
                yield from _model_to_quads(model)

        self._dataset.extend(models_to_quads())
        return self

    @property
    def is_empty(self) -> bool:
        return self._dataset.is_empty

    def _models_by_rdf_type(
        self, *, model_class: type[ModelT], rdf_type: Iri
    ) -> Iterable[ModelT]:
        return (
            model_class(self._resource_set.named_resource(model_iri))
            for model_iri in self._model_iris_by_rdf_type(rdf_type)
        )

    def _model_iris_by_rdf_type(self, rdf_type: Iri) -> Iterable[Iri]:
        return (
            quad.subject
            for quad in self._dataset.match(predicate=RDF.type, object_=rdf_type)
            if isinstance(quad.subject, Iri)
        )
