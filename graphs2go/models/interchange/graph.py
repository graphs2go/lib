from __future__ import annotations

from typing import TYPE_CHECKING

from graphs2go.models import rdf
from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rdflib import URIRef

    from graphs2go.models.interchange.model import Model


class Graph(rdf.Graph):
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    def add(self, model: Model) -> None:
        super()._add(model)

    def add_all(self, models: Iterable[Model]) -> None:
        super()._add_all(models)

    def node_by_uri(self, uri: URIRef) -> Node:
        # For performance reasons, don't check if it's actually a Node
        return Node(resource=self.rdflib_graph.resource(uri))

    def nodes(self, *, rdf_type: URIRef = INTERCHANGE.Node) -> Iterable[Node]:
        return self._models_by_rdf_type(Node, rdf_type=rdf_type)

    def node_uris(self, *, rdf_type: URIRef = INTERCHANGE.Node) -> Iterable[URIRef]:
        return self._model_uris_by_rdf_type(rdf_type=rdf_type)
