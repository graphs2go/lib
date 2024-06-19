from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from rdflib import URIRef, RDF
from graphs2go.models.rdf.resource import Resource

if TYPE_CHECKING:
    from collections.abc import Iterable


class Model:
    class Builder(ABC):
        def __init__(self, resource_builder: Resource.Builder):
            self.__resource_builder = resource_builder

        @abstractmethod
        def build(self) -> Model:
            raise NotImplementedError

        @property
        def _resource_builder(self) -> Resource.Builder:
            return self.__resource_builder

    def __init__(self, resource: Resource):
        self.__resource = resource

    @property
    def identifier(self) -> Resource.Identifier:
        return self.resource.identifier

    @classmethod
    @abstractmethod
    def primary_rdf_type(cls) -> URIRef:
        pass

    @property
    def rdf_types(self) -> Iterable[URIRef]:
        return self.resource.values(RDF.type, Resource.ValueMappers.iri)

    @property
    def resource(self) -> Resource:
        return self.__resource

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier})"

    @property
    def secondary_rdf_types(self) -> Iterable[URIRef]:
        for rdf_type in self.rdf_types:
            if rdf_type != self.primary_rdf_type():
                yield rdf_type
