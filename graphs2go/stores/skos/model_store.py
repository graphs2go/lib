from __future__ import annotations

from typing import TYPE_CHECKING

from graphs2go.models.skos.concept import Concept
from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model
from graphs2go.namespaces import SKOS, SKOSXL
from graphs2go.stores.rdf.model_store import ModelStore as RdfModelStore

if TYPE_CHECKING:
    from collections.abc import Iterable


class ModelStore(RdfModelStore[Model]):
    """
    Non-picklable SKOS graph. Used as an entry point for accessing top-level graph models.
    """

    _CONCEPT_CLASS = Concept
    _CONCEPT_SCHEME_CLASS = ConceptScheme
    _LABEL_CLASS = Label

    def concepts(self) -> Iterable[Concept]:
        return self._models_by_rdf_type(
            model_class=self._CONCEPT_CLASS, rdf_type=SKOS.Concept
        )

    def concept_schemes(self) -> Iterable[ConceptScheme]:
        return self._models_by_rdf_type(
            model_class=self._CONCEPT_SCHEME_CLASS, rdf_type=SKOS.ConceptScheme
        )

    def labels(self) -> Iterable[Label]:
        return self._models_by_rdf_type(
            model_class=self._LABEL_CLASS, rdf_type=SKOSXL.Label
        )
