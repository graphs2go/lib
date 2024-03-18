from __future__ import annotations

from rdflib import RDF


from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.interchange import INTERCHANGE
from typing import TYPE_CHECKING

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
        object_: URIRef,
        predicate: URIRef,
        subject: URIRef,
        uri: URIRef | None = None,
    ) -> Relationship.Builder:
        resource = cls._create_resource(
            uri if uri is not None else hash_urn(subject, predicate, object_)
        )
        resource.add(RDF.object, object_)
        resource.add(RDF.predicate, predicate)
        resource.add(RDF.subject, subject)
        resource.add(RDF.type, RDF.Statement)
        return cls.Builder(resource)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return INTERCHANGE.Relationship
