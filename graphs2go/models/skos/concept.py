from __future__ import annotations

from typing import TYPE_CHECKING, Self

from rdflib import SKOS, Literal, URIRef

from graphs2go.models.label_type import LabelType
from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.labeled_model import LabeledModel

if TYPE_CHECKING:
    from collections.abc import Iterable


class Concept(LabeledModel):
    class Builder(LabeledModel.Builder):
        def add_in_scheme(self, in_scheme: ConceptScheme | URIRef) -> Self:
            if isinstance(in_scheme, ConceptScheme):
                self._resource.add(SKOS.inScheme, in_scheme.uri)
            elif isinstance(in_scheme, URIRef):
                self._resource.add(SKOS.inScheme, in_scheme)
            else:
                raise TypeError(type(in_scheme))
            return self

        def add_relationship(
            self, *, object_: Concept | URIRef, predicate: URIRef
        ) -> Self:
            if predicate == SKOS.inScheme:
                raise ValueError(predicate)

            if isinstance(object_, Concept):
                self._resource.add(predicate, object_.uri)
            elif isinstance(object_, URIRef):
                self._resource.add(predicate, object_)
            else:
                raise TypeError(type(object_))
            return self

        def build(self) -> Concept:
            return Concept(resource=self._resource)

    _CONCEPT_SCHEME_CLASS = ConceptScheme

    @property
    def broader(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.broader,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )  # type: ignore

    @classmethod
    def builder(cls, *, uri: URIRef) -> Builder:
        return cls.Builder(cls._create_resource(uri=uri))

    @property
    def close_match(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.closeMatch,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )  # type: ignore

    @property
    def exact_match(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.exactMatch,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )  # type: ignore

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
    def related(self) -> Iterable[Concept | URIRef]:
        yield from self._values(
            SKOS.broader,
            lambda term: self._map_term_to_model_or_uri(self.__class__, term),
        )  # type: ignore
