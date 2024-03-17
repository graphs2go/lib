from __future__ import annotations
from rdflib import RDF, Graph, Literal, URIRef
from rdflib.resource import Resource
from graphs2go.models.interchange.concept import Concept
from graphs2go.models.interchange.model import Model
from graphs2go.utils.uuid_urn import uuid_urn


class Statement(Model):
    @classmethod
    def create(
        cls, *, object_: Concept | Literal, predicate: URIRef, subject: Concept
    ) -> Statement:
        resource = cls._create_resource(type_=RDF.Statement, uri=uuid_urn())
        if isinstance(object_, Concept):
            resource.add(RDF.object, object_.uri)
        elif isinstance(object_, Literal):
            resource.add(RDF.object, object_)
        resource.add(RDF.predicate, predicate)
        resource.add(RDF.subject, subject.uri)
        return Statement(resource=resource)

    def object_(self) -> Concept | Literal:
        object_ = self.resource.value(RDF.object)
        if isinstance(object_, Literal):
            return object_
        if isinstance(object_, Resource):
            return Concept(resource=object_)
        raise TypeError(type(object_))

    def subject(self) -> Concept:
        subject = self.resource.value(RDF.subject)
        if not isinstance(subject, Resource):
            raise ValueError(  # noqa: TRY004
                "rdf:subject of a relationship is not a resource"
            )
        return Concept(resource=subject)
