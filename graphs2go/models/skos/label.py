from __future__ import annotations

from graphs2go.models import rdf, LabelType
from graphs2go.models.skos.model import Model
from graphs2go.namespaces import RDF, SKOSXL


class Label(Model):
    Type = LabelType

    class Builder(Model.Builder):
        def build(self) -> Label:
            return Label(self._resource_builder.build())

    @classmethod
    def builder(cls, *, literal_form: rdf.Literal, iri: rdf.Iri) -> Builder:
        return cls.Builder(
            rdf.NamedResource.builder(iri=iri)
            .add(RDF.type, SKOSXL.Label)
            .add(SKOSXL.literalForm, literal_form)
        )

    @property
    def literal_form(self) -> rdf.Literal:
        return self.resource.required_value(
            SKOSXL.literalForm, rdf.Resource.ValueMappers.literal
        )
