from __future__ import annotations

from typing import TYPE_CHECKING, Self

from rdflib import SKOS, Literal, URIRef

from graphs2go.models.skos.concept_scheme import ConceptScheme
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model
from graphs2go.namespaces.skosxl import SKOSXL

if TYPE_CHECKING:
    from collections.abc import Iterable


class Concept(Model):
    class Builder(Model.Builder):
        def add_alt_label(self, alt_label: Label | Literal | URIRef) -> Self:
            return self.__add_label(
                label=alt_label,
                skos_predicate=SKOS.altLabel,
                skosxl_predicate=SKOSXL.altLabel,
            )

        def add_broader(self, broader: Concept | URIRef) -> Self:
            return self.add_relationship(object_=broader, predicate=SKOS.broader)

        def add_in_scheme(self, in_scheme: ConceptScheme | URIRef) -> Self:
            if isinstance(in_scheme, ConceptScheme):
                self._resource.add(SKOS.inScheme, in_scheme.uri)
            elif isinstance(in_scheme, URIRef):
                self._resource.add(SKOS.inScheme, in_scheme)
            else:
                raise TypeError(type(in_scheme))
            return self

        def __add_label(
            self,
            *,
            label: Label | Literal | URIRef,
            skos_predicate: URIRef,
            skosxl_predicate: URIRef,
        ) -> Self:
            if isinstance(label, Label):
                self._resource.add(skosxl_predicate, label.uri)
            elif isinstance(label, Literal):
                self._resource.add(skos_predicate, label)
            elif isinstance(label, URIRef):
                self._resource.add(skosxl_predicate, label)
            else:
                raise TypeError(type(label))
            return self

        def add_pref_label(self, pref_label: Label | Literal | URIRef) -> Self:
            return self.__add_label(
                label=pref_label,
                skos_predicate=SKOS.prefLabel,
                skosxl_predicate=SKOSXL.prefLabel,
            )

        def add_relationship(
            self, *, object_: Concept | URIRef, predicate: URIRef
        ) -> Self:
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
    _LABEL_CLASS = Label

    @property
    def alt_label(self) -> Iterable[Label | Literal]:
        yield from self._values(SKOS.altLabel, self._map_term_to_literal)
        yield from self._values(
            SKOSXL.altLabel,
            lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
        )  # type: ignore

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

    @property
    def pref_label(self) -> Iterable[Label | Literal]:
        yield from self._values(SKOS.prefLabel, self._map_term_to_literal)
        yield from self._values(
            SKOSXL.prefLabel,
            lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
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
