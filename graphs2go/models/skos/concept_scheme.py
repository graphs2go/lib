from __future__ import annotations

from rdflib import SKOS, URIRef

from graphs2go.models.skos.labeled_model import LabeledModel


class ConceptScheme(LabeledModel):
    class Builder(LabeledModel.Builder):
        def build(self) -> ConceptScheme:
            return ConceptScheme(resource=self._resource)

    @classmethod
    def builder(cls, *, iri: URIRef) -> Builder:
        return cls.Builder(cls._create_resource(iri=iri))

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return SKOS.ConceptScheme
