from __future__ import annotations

from typing import TYPE_CHECKING

from graphs2go.models.skos.model import Model
from graphs2go.namespaces.skosxl import SKOSXL

if TYPE_CHECKING:
    from rdflib import Literal, URIRef


class Label(Model):
    class Builder(Model.Builder):
        def build(self) -> Label:
            return Label(resource=self._resource)

    @classmethod
    def builder(cls, *, literal_form: Literal, uri: URIRef) -> Builder:
        resource = cls._create_resource(uri=uri)
        resource.add(SKOSXL.literalForm, literal_form)
        return cls.Builder(resource)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return SKOSXL.Label

    @property
    def literal_form(self) -> Literal:
        return self._required_value(SKOSXL.literalForm, self._map_term_to_literal)
