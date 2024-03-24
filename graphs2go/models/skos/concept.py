from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from rdflib import SKOS, URIRef

from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.labeled_model import LabeledModel

if TYPE_CHECKING:
    from collections.abc import Iterable


class Concept(LabeledModel):
    _CONCEPT_SCHEME_CLASS = ConceptScheme

    # https://www.w3.org/TR/skos-reference/#L4160
    SEMANTIC_RELATION_PREDICATES: ClassVar[frozenset[URIRef]] = frozenset(
        [
            SKOS.broader,
            SKOS.broadMatch,
            SKOS.broaderTransitive,
            SKOS.closeMatch,
            SKOS.exactMatch,
            SKOS.narrower,
            SKOS.narrowerTransitive,
            SKOS.narrowMatch,
            SKOS.related,
            SKOS.relatedMatch,
        ]
    )

    class Builder(LabeledModel.Builder):
        def add_in_scheme(self, in_scheme: ConceptScheme | URIRef) -> Self:
            return self._add(SKOS.inScheme, in_scheme)

        def add_semantic_relation(
            self, *, object_: Concept | URIRef, predicate: URIRef
        ) -> Self:
            if predicate not in Concept.SEMANTIC_RELATION_PREDICATES:
                raise ValueError(f"{predicate} is not a semantic relation")

            return self._add(predicate, object_)

        def build(self) -> Concept:
            return Concept(resource=self._resource)

    @classmethod
    def builder(cls, *, uri: URIRef) -> Builder:
        return cls.Builder(cls._create_resource(uri=uri))

    @property
    def in_scheme(self) -> Iterable[ConceptScheme | URIRef]:
        yield from self._values(
            SKOS.inScheme,
            lambda term: self._map_term_to_model_or_uri(
                self._CONCEPT_SCHEME_CLASS, term
            ),
        )  # type: ignore

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return SKOS.Concept

    @property
    def semantic_relations(self) -> Iterable[tuple[URIRef, Concept | URIRef]]:
        for predicate in self.SEMANTIC_RELATION_PREDICATES:
            for value in self._values(
                predicate,
                lambda term: self._map_term_to_model_or_uri(self.__class__, term),
            ):  # type: ignore
                yield predicate, value  # type: ignore
