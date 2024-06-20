from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import RDF
from returns.maybe import Maybe, Nothing

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
            return Relationship(self._resource_builder.build())

    @classmethod
    def builder(
        cls,
        subject: rdf.NamedModel | URIRef,
        predicate: URIRef,
        object_: rdf.NamedModel | URIRef,
        *,
        iri: Maybe[URIRef] = Nothing,
    ) -> Relationship.Builder:
        object_iri = object_.iri if isinstance(object_, rdf.NamedModel) else object_
        subject_iri = subject.iri if isinstance(subject, rdf.NamedModel) else subject

        resource_builder = rdf.NamedResource.builder(
            iri=iri.or_else_call(lambda: hash_urn(subject_iri, predicate, object_iri))
        )
        resource_builder.add(RDF.object, object_iri)
        resource_builder.add(RDF.predicate, predicate)
        resource_builder.add(RDF.subject, subject_iri)
        resource_builder.add(RDF.type, INTERCHANGE.Relationship)
        resource_builder.add(RDF.type, RDF.Statement)
        # Add direct statements for ease of querying
        # (s, p, o)
        # resource.graph.add((subject_iri, predicate, object_iri))
        # Node -> Relationship instances
        resource_builder.graph.add(
            (subject_iri, INTERCHANGE.relationship, resource_builder.identifier)
        )

        return cls.Builder(resource_builder)

    @property
    def object(self) -> URIRef:
        return self.resource.required_value(RDF.object, rdf.Resource.ValueMappers.iri)

    @property
    def predicate(self) -> URIRef:
        return self.resource.required_value(
            RDF.predicate, rdf.Resource.ValueMappers.iri
        )

    @property
    def subject(self) -> URIRef:
        return self.resource.required_value(RDF.subject, rdf.Resource.ValueMappers.iri)
