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
        def add_rdf_type(self, rdf_type: URIRef) -> Self:
            return self._resource_builder.add(RDF.type, rdf_type)

        def build(self) -> Node:
            return Node(self._resource_builder.build())

    @classmethod
    def builder(cls, *, iri: URIRef) -> Node.Builder:
        return cls.Builder(rdf.NamedResource.builder(iri=iri))

    def __dependent_models(
        self, model_class: type[_ModelT], predicate: URIRef
    ) -> Iterable[_ModelT]:
        for resource in self.resource.values(
            predicate, rdf.Resource.ValueMappers.named_resource, unique=True
        ):
            yield model_class(resource)

    @property
    def labels(self) -> Iterable[Label]:
        return self.__dependent_models(Label, INTERCHANGE.label)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return INTERCHANGE.Node

    @property
    def properties(self) -> Iterable[Property]:
        return self.__dependent_models(Property, INTERCHANGE.property)

    @property
    def relationships(self) -> Iterable[Relationship]:
        return self.__dependent_models(Relationship, INTERCHANGE.relationship)
