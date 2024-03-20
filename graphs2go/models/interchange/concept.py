from __future__ import annotations

from rdflib import RDF, SKOS, URIRef

from graphs2go.models.interchange.node import Node


class Concept(Node):
    """
    Top-level nodes in the interchange graph that are equivalent to SKOS Concept's.
    """

    class Builder(Node.Builder):
        def build(self) -> Concept:
            return Concept(resource=self._resource)

    @classmethod
    def builder(cls, *, uri: URIRef) -> Concept.Builder:
        resource = cls._create_resource(uri)
        resource.add(RDF.type, Node.rdf_type_uri())
        return cls.Builder(resource)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return SKOS.Concept
