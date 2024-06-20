from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import URIRef

from graphs2go.models import rdf
from graphs2go.models.interchange.model import Model
from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE

if TYPE_CHECKING:
    from collections.abc import Iterable


class Graph(rdf.Graph[Model]):
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    def node_by_iri(self, iri: URIRef) -> Node:
        # For performance reasons, don't check if it's actually a Node
        return Node(rdf.NamedResource(graph=self.rdflib_graph, iri=iri))

    def nodes(self) -> Iterable[Node]:
        return self._models_by_rdf_type(model_class=Node, rdf_type=INTERCHANGE.Node)

    def nodes_by_type(self, type_: URIRef) -> Iterable[Node]:
        return (
            Node(resource=rdf.NamedResource(graph=self.rdflib_graph, iri=node_iri))
            for node_iri in self.node_iris_by_type(type_)
        )

    def node_iris(self) -> Iterable[URIRef]:
        return self._model_iris_by_rdf_type(INTERCHANGE.Node)

    def node_iris_by_type(self, type_: URIRef) -> Iterable[URIRef]:
        return (
            node_iri
            for node_iri in self.__rdflib_graph.subjects(
                predicate=INTERCHANGE.nodeType,
                object=type_,
                unique=True,
            )
            if isinstance(node_iri, URIRef)
        )
