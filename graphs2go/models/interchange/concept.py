from __future__ import annotations

from rdflib import SKOS, URIRef

from graphs2go.models.interchange.model import Model


class Concept(Model):
    @classmethod
    def builder(cls, *, uri: URIRef) -> Concept.Builder:
        return cls.builder(cls._create_resource(uri))

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return SKOS.Concept
