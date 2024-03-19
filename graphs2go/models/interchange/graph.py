from __future__ import annotations

from typing import TYPE_CHECKING

import rdflib

from graphs2go.models import rdf
from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.models.interchange.model import Model


class Graph(rdf.Graph):
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    def add(self, model: Model) -> None:
        self._rdflib_graph += model.resource.graph

    @property
    def nodes(self) -> Iterable[Node]:
        for subject_uri in self._rdflib_graph.subjects(
            predicate=rdflib.RDF.type, object=INTERCHANGE.Node
        ):
            yield Node(resource=self._rdflib_graph.resource(subject_uri))
