from __future__ import annotations

from typing import TYPE_CHECKING, Self, TypeVar

from rdflib import RDF, URIRef

from graphs2go.models import rdf
from graphs2go.models.interchange.label import Label
from graphs2go.models.interchange.model import Model
from graphs2go.models.interchange.property import Property
from graphs2go.models.interchange.relationship import Relationship
from graphs2go.namespaces.interchange import INTERCHANGE

if TYPE_CHECKING:
    from collections.abc import Iterable

_ModelT = TypeVar("_ModelT", bound="Model")


class Node(Model):
    """
    Top-level node in the interchange graph, equivalent to a node in a labeled property graph.
    """

    class Builder(Model.Builder):
        def add_type(self, type_: URIRef) -> Self:
            self._resource_builder.add(INTERCHANGE.nodeType, type_)
            return self

        def build(self) -> Node:
            return Node(self._resource_builder.build())

    @classmethod
    def builder(cls, iri: URIRef) -> Node.Builder:
        return cls.Builder(
            rdf.NamedResource.builder(iri=iri).add(RDF.type, INTERCHANGE.Node)
        )

    def __dependent_models(
        self, model_class: type[_ModelT], predicate: URIRef
    ) -> Iterable[_ModelT]:
        resource: rdf.NamedResource
        for resource in self.resource.values(
            predicate, rdf.Resource.ValueMappers.named_resource, unique=True
        ):
            yield model_class(resource)

    def labels(self) -> Iterable[Label]:
        return self.__dependent_models(Label, INTERCHANGE.label)

    def properties(self) -> Iterable[Property]:
        return self.__dependent_models(Property, INTERCHANGE.property)

    def relationships(self) -> Iterable[Relationship]:
        return self.__dependent_models(Relationship, INTERCHANGE.relationship)

    @property
    def types(self) -> tuple[URIRef, ...]:
        return tuple(
            self.resource.values(INTERCHANGE.nodeType, rdf.Resource.ValueMappers.iri)
        )
