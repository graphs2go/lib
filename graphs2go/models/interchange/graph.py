from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar


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
    def concepts(self) -> Iterable[Concept]:
        return self._models_by_rdf_type(Concept)

    @property
    def nodes(self) -> Iterable[Node]:
        return self._models_by_rdf_type(self.__NODE_CLASSES)
