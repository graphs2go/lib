from __future__ import annotations
from rdflib import SKOS, URIRef

from graphs2go.models.skos.model import Model


class ConceptScheme(Model):
    class Builder(Model.Builder):
        def build(self) -> ConceptScheme:
            return ConceptScheme(resource=self._resource)

    @classmethod
    def builder(cls, *, uri: URIRef) -> Builder:
        return cls.Builder(cls._create_resource(uri=uri))

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return SKOS.ConceptScheme
