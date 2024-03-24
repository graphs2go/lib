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
        super().add(model)

    def add_all(self, models: Iterable[Model]) -> None:
        super().add_all(models)

    def nodes(self, *, rdf_type: URIRef = INTERCHANGE.Node) -> Iterable[Node]:
        return self._models_by_rdf_type(Node, rdf_type=rdf_type)
