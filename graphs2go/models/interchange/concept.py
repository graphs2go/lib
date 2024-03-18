from __future__ import annotations
from rdflib import RDF, SKOS, URIRef
from graphs2go.models.interchange.node import Node


class Concept(Node):
    """
    Top-level nodes in the interchange graph that are equivalent to SKOS Concept's.
    """

    @classmethod
    def builder(cls, *, uri: URIRef) -> Concept.Builder:
        resource = cls._create_resource(uri)
        resource.add(RDF.type, SKOS.Concept)
        return cls.Builder(resource)
