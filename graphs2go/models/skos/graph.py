from __future__ import annotations

from typing import TYPE_CHECKING


from graphs2go.models import rdf

if TYPE_CHECKING:
    from graphs2go.models.skos.model import Model


class Graph(rdf.Graph):
    """
    Non-picklable SKOS graph. Used as an entry point for accessing top-level graph models.
    """

    def add(self, model: Model) -> None:
        self._rdflib_graph += model.resource.graph
