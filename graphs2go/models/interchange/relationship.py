from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import RDF

from graphs2go.models import rdf
from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.utils.hash_urn import hash_urn

if TYPE_CHECKING:
    from rdflib import URIRef


class Relationship(Model):
    """
    A top-level relationship between top-level Nodes, equivalent to a relationship in a labeled property graph.
    """

    class Builder(Model.Builder):
        def build(self) -> Relationship:
            return Relationship(resource=self._resource)

    @classmethod
    def builder(
        cls,
        *,
        object_: rdf.Model | URIRef,
        predicate: URIRef,
        subject: rdf.Model | URIRef,
        uri: URIRef | None = None,
    ) -> Relationship.Builder:
        object_uri = object_.uri if isinstance(object_, rdf.Model) else object_
        subject_uri = subject.uri if isinstance(subject, rdf.Model) else subject

        resource = cls._create_resource(
            uri if uri is not None else hash_urn(subject_uri, predicate, object_uri)
        )
        resource.add(RDF.object, object_uri)
        resource.add(RDF.predicate, predicate)
        resource.add(RDF.subject, subject_uri)
        resource.add(RDF.type, RDF.Statement)
        # Add direct statements for ease of querying
        # (s, p, o)
        resource.graph.add((subject_uri, predicate, object_uri))
        # Node -> Relationship instances
        resource.graph.add((subject_uri, INTERCHANGE.relationship, resource.identifier))

        return cls.Builder(resource)

    @property
    def object(self) -> URIRef:
        return self._required_value(RDF.object, self._map_term_to_uri)

    @property
    def predicate(self) -> URIRef:
        return self._required_value(RDF.predicate, self._map_term_to_uri)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return INTERCHANGE.Relationship

    @property
    def subject(self) -> URIRef:
        return self._required_value(RDF.subject, self._map_term_to_uri)
