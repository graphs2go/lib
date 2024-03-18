from __future__ import annotations

from rdflib import SKOS, URIRef, Literal
from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model
from graphs2go.namespaces.skosxl import SKOSXL
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


class Concept(Model):
    _CONCEPT_SCHEME_CLASS = ConceptScheme
    _LABEL_CLASS = Label

    @property
    def alt_label(self) -> Iterable[Label | Literal]:
        yield from self._values(SKOS.altLabel, self._map_term_to_literal)
        yield from self._values(
            SKOSXL.altLabel,
            lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
        )

    @property
    def broader(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.broader,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )

    @property
    def close_match(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.closeMatch,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )

    @property
    def exact_match(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.exactMatch,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )

    @property
    def in_scheme(self) -> Iterable[ConceptScheme | URIRef]:
        yield from self._values(
            SKOS.ConceptScheme,
            lambda term: self._map_term_to_model_or_uri(
                self._CONCEPT_SCHEME_CLASS, term
            ),
        )

    @property
    def pref_label(self) -> Iterable[Label | Literal]:
        yield from self._values(SKOS.prefLabel, self._map_term_to_literal)
        yield from self._values(
            SKOSXL.prefLabel,
            lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
        )

    @property
    def related(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.broader,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )
