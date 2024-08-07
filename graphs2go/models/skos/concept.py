from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self

from rdflib import RDF, SKOS, Literal, URIRef

from graphs2go.models import rdf
from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.labeled_model import LabeledModel

if TYPE_CHECKING:
    from collections.abc import Iterable


class Concept(LabeledModel):
    _CONCEPT_SCHEME_CLASS = ConceptScheme

    # https://www.w3.org/TR/skos-reference/#notes
    NOTE_PREDICATES: ClassVar[frozenset[URIRef]] = frozenset(
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
    SEMANTIC_RELATION_PREDICATES: ClassVar[frozenset[URIRef]] = frozenset(
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

    class Builder(LabeledModel.Builder):
        def add_in_scheme(self, in_scheme: URIRef) -> Self:
            self._resource_builder.add(SKOS.inScheme, in_scheme)
            return self

        def add_notation(self, notation: Literal) -> Self:
            self._resource_builder.add(SKOS.notation, notation)
            return self

        def add_note(self, predicate: URIRef, object_: Literal) -> Self:
            if predicate not in Concept.NOTE_PREDICATES:
                raise ValueError(f"{predicate} is not a note predicate")

            self._resource_builder.add(predicate, object_)
            return self

        def add_semantic_relation(self, predicate: URIRef, object_: URIRef) -> Self:
            if predicate not in Concept.SEMANTIC_RELATION_PREDICATES:
                raise ValueError(f"{predicate} is not a semantic relation")

            self._resource_builder.add(predicate, object_)
            return self

        def add_top_concept_of(self, top_concept_of: URIRef) -> Self:
            self._resource_builder.add(SKOS.topConceptOf, top_concept_of)
            return self

        def build(self) -> Concept:
            return Concept(self._resource_builder.build())

    @classmethod
    def builder(cls, *, iri: URIRef) -> Builder:
        return cls.Builder(
            rdf.NamedResource.builder(iri=iri).add(RDF.type, SKOS.Concept)
        )

    def in_schemes(self) -> Iterable[ConceptScheme]:
        resource: rdf.NamedResource
        for resource in self.resource.values(
            SKOS.inScheme, rdf.Resource.ValueMappers.named_resource
        ):
            yield self._CONCEPT_SCHEME_CLASS(resource)

    def notations(self) -> Iterable[Literal]:
        yield from self.resource.values(
            SKOS.notation, rdf.Resource.ValueMappers.literal
        )

    def notes(self) -> Iterable[tuple[URIRef, Literal]]:
        for predicate in self.NOTE_PREDICATES:
            value: Literal
            for value in self.resource.values(
                predicate, rdf.Resource.ValueMappers.literal
            ):
                yield predicate, value

    def semantic_relations(self) -> Iterable[tuple[URIRef, Concept]]:
        for predicate in self.SEMANTIC_RELATION_PREDICATES:
            resource: rdf.NamedResource
            for resource in self.resource.values(
                predicate, rdf.Resource.ValueMappers.named_resource
            ):
                yield predicate, self.__class__(resource)
