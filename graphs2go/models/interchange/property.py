from __future__ import annotations

from rdflib import RDF, Literal, URIRef

from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.utils.hash_urn import hash_urn


class Property(Model):
    """
    A node->literal relationship, equivalent to a property in a labeled property graph.
    """

    class Builder(Model.Builder):
        def build(self) -> Property:
            return Property(resource=self._resource)

    @classmethod
    def builder(
        cls,
        *,
        predicate: URIRef,
        object_: Literal,
        subject: URIRef,
        uri: URIRef | None = None,
    ) -> Property.Builder:
        resource = cls._create_resource(
            uri if uri is not None else hash_urn(subject, predicate, object_)
        )
        resource.add(RDF.object, object_)
        resource.add(RDF.predicate, predicate)
        resource.add(RDF.subject, subject)
        resource.add(RDF.type, RDF.Statement)
        # Add direct statements for ease of querying
        # (s, p, o)
        resource.graph.add((subject, predicate, object_))
        # Node -> Property instance
        resource.graph.add((subject, INTERCHANGE.property, resource.identifier))
        return cls.Builder(resource)

    @property
    def object(self) -> Literal:
        return self._required_value(RDF.object, self._map_term_to_literal)

    @property
    def predicate(self) -> URIRef:
        return self._required_value(RDF.predicate, self._map_term_to_uri)

    @property
    def subject(self) -> URIRef:
        return self._required_value(RDF.subject, self._map_term_to_uri)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return INTERCHANGE.Property
