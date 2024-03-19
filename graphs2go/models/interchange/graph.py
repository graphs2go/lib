from __future__ import annotations

from typing import TYPE_CHECKING

import rdflib

from graphs2go.models.persistent_rdf_graph import PersistentRdfGraph
from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.models.interchange.model import Model


class Graph(PersistentRdfGraph):
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    def add(self, model: Model) -> None:
        self.__rdf_graph += model.resource.graph

    @property
    def nodes(self) -> Iterable[Node]:
        for subject_uri in self.__rdf_graph.subjects(
            predicate=rdflib.RDF.type, object=INTERCHANGE.Node
        ):
            yield Node(resource=self.__rdf_graph.resource(subject_uri))
