from __future__ import annotations

from typing import TYPE_CHECKING

from graphs2go.models import rdf
from graphs2go.models.skos.concept import Concept
from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.label import Label

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.models.skos.model import Model


class Graph(rdf.Graph):
    """
    Non-picklable SKOS graph. Used as an entry point for accessing top-level graph models.
    """

    _CONCEPT_CLASS = Concept
    _CONCEPT_SCHEME_CLASS = ConceptScheme
    _LABEL_CLASS = Label

    def add(self, model: Model) -> None:
        super().add(model)

    def add_all(self, models: Iterable[Model]) -> None:
        super().add_all(models)

    @property
    def concepts(self) -> Iterable[Concept]:
        return self._models_by_rdf_type(self._CONCEPT_CLASS)

    @property
    def concept_schemes(self) -> Iterable[ConceptScheme]:
        return self._models_by_rdf_type(self._CONCEPT_SCHEME_CLASS)

    @property
    def labels(self) -> Iterable[Label]:
        return self._models_by_rdf_type(self._LABEL_CLASS)
