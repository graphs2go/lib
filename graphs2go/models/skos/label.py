from __future__ import annotations

from typing import TYPE_CHECKING

from graphs2go.models import rdf
from graphs2go.models.label_type import LabelType
from graphs2go.models.skos.model import Model
from graphs2go.namespaces.skosxl import SKOSXL

if TYPE_CHECKING:
    from rdflib import Literal, URIRef


class Label(Model):
    Type = LabelType

    class Builder(Model.Builder):
        def build(self) -> Label:
            return Label(self._resource_builder.build())

    @classmethod
    def builder(cls, *, literal_form: Literal, iri: URIRef) -> Builder:
        resource_builder = rdf.NamedResource.builder(iri=iri)
        resource_builder.add(SKOSXL.literalForm, literal_form)
        return cls.Builder(resource_builder)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return SKOSXL.Label

    @property
    def literal_form(self) -> Literal:
        return self.resource.required_value(
            SKOSXL.literalForm, rdf.Resource.ValueMappers.literal
        )
