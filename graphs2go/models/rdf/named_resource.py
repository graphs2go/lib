from __future__ import annotations

from typing import TYPE_CHECKING

from returns.maybe import Maybe, Nothing
from returns.pipeline import is_successful

from graphs2go.models.rdf.resource import Resource

if TYPE_CHECKING:
    from graphs2go.models.rdf.dataset import Dataset
    from graphs2go.models.rdf.iri import Iri


class NamedResource(Resource):
    class Builder(Resource.Builder):
        def __init__(self, *, dataset: Dataset, iri: Iri):
            Resource.Builder.__init__(self, dataset=dataset, identifier=iri)
            self.__iri = iri

        def build(self) -> NamedResource:
            return NamedResource(dataset=self.__dataset, iri=self.__iri)

        @property
        def iri(self) -> Iri:
            return self.__iri

    def __init__(self, *, dataset: Dataset, iri: Iri):
        Resource.__init__(self, dataset=dataset, identifier=iri)
        self.__iri = iri

    @classmethod
    def builder(cls, *, iri: Iri, dataset: Maybe[Dataset] = Nothing) -> Builder:  # type: ignore
        if is_successful(dataset):
            return cls.Builder(dataset=dataset.unwrap(), iri=iri)

        from graphs2go.models.rdf.oxigraph_dataset import OxigraphDataset

        return cls.Builder(dataset=OxigraphDataset(), iri=iri)

    @property
    def iri(self) -> Iri:
        return self.__iri
