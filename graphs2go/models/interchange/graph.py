from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rdflib import RDF, URIRef

from graphs2go.models import rdf
from graphs2go.models.interchange.concept import Concept
from graphs2go.models.interchange.node import Node

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.models.interchange.model import Model


class Graph(rdf.Graph):
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    __NODE_CLASSES: ClassVar[tuple[type[Node], ...]] = (Concept, Node)

    def add(self, model: Model) -> None:
        self._rdflib_graph += model.resource.graph

    @property
    def nodes(self) -> Iterable[Node]:
        yielded_node_uris: set[URIRef] = set()
        for node_class in self.__NODE_CLASSES:
            for node_uri in self._rdflib_graph.subjects(
                predicate=RDF.type, object=node_class.rdf_type_uri(), unique=True
            ):
                if not isinstance(node_uri, URIRef):
                    continue
                if node_uri in yielded_node_uris:
                    continue

                yield node_class(resource=self._rdflib_graph.resource(node_uri))
                yielded_node_uris.add(node_uri)
