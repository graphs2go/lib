from __future__ import annotations

from returns.maybe import Maybe, Nothing

from graphs2go.models import rdf
from graphs2go.models.interchange.model import Model
from graphs2go.namespaces import INTERCHANGE, RDF
from graphs2go.utils.hash_urn import hash_urn


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
        subject: rdf.NamedModel | rdf.Iri,
        predicate: rdf.Iri,
        object_: rdf.NamedModel | rdf.Iri,
        *,
        iri: Maybe[rdf.Iri] = Nothing,
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
        resource_builder.dataset.add(
            rdf.Quad(subject_iri, INTERCHANGE.relationship, resource_builder.identifier)
        )

        return cls.Builder(resource_builder)

    @property
    def object(self) -> rdf.Iri:
        return self.resource.value(RDF.object).unwrap().to_iri().unwrap()

    @property
    def predicate(self) -> rdf.Iri:
        return self.resource.value(RDF.predicate).unwrap().to_iri().unwrap()

    @property
    def subject(self) -> rdf.Iri:
        return self.resource.value(RDF.subject).unwrap().to_iri().unwrap()
