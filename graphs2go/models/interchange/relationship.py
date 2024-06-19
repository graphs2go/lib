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
        iri: URIRef | None = None,
    ) -> Relationship.Builder:
        object_iri = object_.iri if isinstance(object_, rdf.Model) else object_
        subject_iri = subject.iri if isinstance(subject, rdf.Model) else subject

        resource = cls._create_resource(
            iri if iri is not None else hash_urn(subject_iri, predicate, object_iri)
        )
        resource.add(RDF.object, object_iri)
        resource.add(RDF.predicate, predicate)
        resource.add(RDF.subject, subject_iri)
        resource.add(RDF.type, RDF.Statement)
        # Add direct statements for ease of querying
        # (s, p, o)
        # resource.graph.add((subject_iri, predicate, object_iri))
        # Node -> Relationship instances
        resource.graph.add((subject_iri, INTERCHANGE.relationship, resource.identifier))

        return cls.Builder(resource)

    @property
    def object(self) -> URIRef:
        return self._required_value(RDF.object, self._map_term_to_iri)

    @property
    def predicate(self) -> URIRef:
        return self._required_value(RDF.predicate, self._map_term_to_iri)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return INTERCHANGE.Relationship

    @property
    def subject(self) -> URIRef:
        return self._required_value(RDF.subject, self._map_term_to_iri)
