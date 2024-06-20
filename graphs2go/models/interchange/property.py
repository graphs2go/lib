from __future__ import annotations

from rdflib import RDF, Literal, URIRef
from returns.maybe import Maybe, Nothing

from graphs2go.models import rdf
from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.utils.hash_urn import hash_urn


class Property(Model):
    """
    A node->literal relationship, equivalent to a property in a labeled property graph.
    """

    class Builder(Model.Builder):
        def build(self) -> Property:
            return Property(self._resource_builder.build())

    @classmethod
    def builder(
        cls,
        subject: rdf.NamedModel | URIRef,
        predicate: URIRef,
        object_: Literal,
        *,
        iri: Maybe[URIRef] = Nothing,
    ) -> Property.Builder:
        subject_iri = subject.iri if isinstance(subject, rdf.NamedModel) else subject

        resource_builder = rdf.NamedResource.builder(
            iri=iri.or_else_call(lambda: hash_urn(subject_iri, predicate, object_))
        )
        resource_builder.add(RDF.object, object_)
        resource_builder.add(RDF.predicate, predicate)
        resource_builder.add(RDF.subject, subject_iri)
        resource_builder.add(RDF.type, INTERCHANGE.Property)
        resource_builder.add(RDF.type, RDF.Statement)
        # Add direct statements for ease of querying
        # (s, p, o)
        # resource.graph.add((subject_iri, predicate, object_))
        # Node -> Property instance
        resource_builder.graph.add(
            (subject_iri, INTERCHANGE.property, resource_builder.identifier)
        )

        return cls.Builder(resource_builder)

    @property
    def object(self) -> Literal:
        return self.resource.required_value(
            RDF.object, rdf.Resource.ValueMappers.literal
        )

    @property
    def predicate(self) -> URIRef:
        return self.resource.required_value(
            RDF.predicate, rdf.Resource.ValueMappers.iri
        )

    @property
    def subject(self) -> URIRef:
        return self.resource.required_value(RDF.subject, rdf.Resource.ValueMappers.iri)
