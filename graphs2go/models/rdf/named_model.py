from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, cast

from graphs2go.models.rdf.model import Model
from graphs2go.models.rdf.named_resource import NamedResource

if TYPE_CHECKING:
    from rdflib import URIRef


class NamedModel(Model):
    class Builder(Model.Builder):
        def __init__(self, resource_builder: NamedResource.Builder):
            Model.Builder.__init__(self, resource_builder)

        @property
        def _resource_builder(self) -> NamedResource.Builder:
            return cast(NamedResource.Builder, super()._resource_builder)

        @abstractmethod
        def build(self) -> NamedModel:
            raise NotImplementedError

    @property
    def resource(self) -> NamedResource:
        return cast(NamedResource, super().resource)

    @property
    def identifier(self) -> URIRef:
        return self.resource.iri

    @property
    def iri(self) -> URIRef:
        return self.resource.iri
