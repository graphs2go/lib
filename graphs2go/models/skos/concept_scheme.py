from __future__ import annotations

from typing import Self

from graphs2go.models import rdf
from graphs2go.namespaces import RDF, SKOS
from graphs2go.models.skos.labeled_model import LabeledModel


class ConceptScheme(LabeledModel):
    class Builder(LabeledModel.Builder):
        def add_top_concept(self, top_concept: rdf.Iri) -> Self:
            self._resource_builder.add(SKOS.hasTopConcept, top_concept)
            return self

        def build(self) -> ConceptScheme:
            return ConceptScheme(self._resource_builder.build())

    @classmethod
    def builder(cls, *, iri: rdf.Iri) -> Builder:
        return cls.Builder(
            rdf.NamedResource.builder(iri=iri).add(RDF.type, SKOS.ConceptScheme)
        )
