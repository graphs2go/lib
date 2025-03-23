from graphs2go.models.rdf.dataset import Dataset
from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.named_resource import NamedResource
from graphs2go.models.rdf.resource import Resource


class ResourceSet:
    def __init__(self, *, dataset: Dataset):
        self.__dataset = dataset

    @property
    def dataset(self) -> Dataset:
        return self.__dataset

    def named_resource(self, iri: Iri) -> NamedResource:
        return NamedResource(dataset=self.__dataset, iri=iri)

    def resource(self, identifier: Resource.Identifier) -> Resource:
        return Resource(dataset=self.__dataset, identifier=identifier)
