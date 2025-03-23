from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from graphs2go.models import rdf
from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.resource import Resource
from graphs2go.namespaces import RDF, SKOS
from graphs2go.utils import success_values

if TYPE_CHECKING:
    from collections.abc import Iterable


class Concept(Resource):
    _CONCEPT_SCHEME_CLASS = ConceptScheme

    # https://www.w3.org/TR/skos-reference/#notes
    NOTE_PREDICATES: ClassVar[frozenset[rdf.Iri]] = frozenset(
        (
            SKOS.changeNote,
            SKOS.editorialNote,
            SKOS.definition,
            SKOS.example,
            SKOS.historyNote,
            SKOS.note,
            SKOS.scopeNote,
        )
    )

    # https://www.w3.org/TR/skos-reference/#L4160
    SEMANTIC_RELATION_PREDICATES: ClassVar[frozenset[rdf.Iri]] = frozenset(
        (
            # Don't include skos:semanticRelation or skos:mappingRelation
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
        )
    )

    class Builder(Resource.Builder):
        def add_in_scheme(self, in_scheme: rdf.Iri) -> Self:
            self._resource_builder.add(SKOS.inScheme, in_scheme)
            return self

        def add_notation(self, notation: rdf.Literal) -> Self:
            self._resource_builder.add(SKOS.notation, notation)
            return self

        def add_note(self, predicate: rdf.Iri, object_: rdf.Literal) -> Self:
            if predicate not in Concept.NOTE_PREDICATES:
                raise ValueError(f"{predicate} is not a note predicate")

            self._resource_builder.add(predicate, object_)
            return self

        def add_semantic_relation(self, predicate: rdf.Iri, object_: rdf.Iri) -> Self:
            if predicate not in Concept.SEMANTIC_RELATION_PREDICATES:
                raise ValueError(f"{predicate} is not a semantic relation")

            self._resource_builder.add(predicate, object_)
            return self

        def add_top_concept_of(self, top_concept_of: rdf.Iri) -> Self:
            self._resource_builder.add(SKOS.topConceptOf, top_concept_of)
            return self

        def build(self) -> Concept:
            return Concept(self._resource_builder.build())

    @classmethod
    def builder(cls, *, iri: rdf.Iri) -> Builder:
        return cls.Builder(
            rdf.NamedResource.builder(iri=iri).add(RDF.type, SKOS.Concept)
        )

    def in_schemes(self) -> Iterable[ConceptScheme]:
        yield from success_values(
            value.to_named_resource().map(self._CONCEPT_SCHEME_CLASS)
            for value in self.resource.values(SKOS.inScheme)
        )

    def notations(self) -> Iterable[rdf.Literal]:
        yield from success_values(
            value.to_literal() for value in self.resource.values(SKOS.notation)
        )

    def notes(self) -> Iterable[tuple[rdf.Iri, rdf.Literal]]:
        for predicate in self.NOTE_PREDICATES:
            for literal in success_values(
                value.to_literal() for value in self.resource.values(predicate)
            ):
                yield predicate, literal

    def semantic_relations(self) -> Iterable[tuple[rdf.Iri, Concept]]:
        for predicate in self.SEMANTIC_RELATION_PREDICATES:
            for resource in success_values(
                value.to_named_resource() for value in self.resource.values(predicate)
            ):
                yield predicate, self.__class__(resource)
