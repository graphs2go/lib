from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import RDF, BNode, Literal, URIRef

if TYPE_CHECKING:
    from rdflib.resource import Resource


class ResourceBuilder:
    """
    A class that helps build up an rdflib Resource in a graph.

    The "builder" nomenclature is slightly misleading in that this class and its subclasses don't implement a true builder pattern.
    Their add_ methods are mutating the rdflib Resource/Graphs.
    """

    def __init__(self, *, resource: Resource):
        self._resource = resource

    def _add_reified_statement(
        self,
        predicate: URIRef,
        object_: Literal | URIRef,
        reifications: tuple[tuple[URIRef, Literal | URIRef], ...],
    ) -> ResourceBuilder:
        statement_resource = self._resource.graph.resource(BNode())
        statement_resource.add(RDF.type, RDF.Statement)
        statement_resource.add(RDF.subject, self._resource)
        statement_resource.add(RDF.predicate, predicate)
        statement_resource.add(RDF.object, object_)
        for reification_predicate, reification_object in reifications:
            statement_resource.add(reification_predicate, reification_object)
        return self

    def build(self) -> Resource:
        return self._resource
