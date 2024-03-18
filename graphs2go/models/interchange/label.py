from __future__ import annotations
from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.skosxl import SKOSXL
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rdflib import Literal, URIRef


class Label(Model):
    @classmethod
    def builder(cls, *, literal_form: Literal, uri: URIRef) -> Label.Builder:
        resource = cls._create_resource(uri=uri)
        resource.add(SKOSXL.literalForm, literal_form)
        return cls.Builder(resource)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return SKOSXL.Label
