from collections.abc import Iterable
from typing import Self

from rdflib import SKOS, Literal, URIRef

from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model
from graphs2go.namespaces.skosxl import SKOSXL


class LabeledModel(Model):
    class Builder(Model.Builder):
        def add_alt_label(self, alt_label: Label | Literal | URIRef) -> Self:
            return self.__add_label(
                label=alt_label,
                skos_predicate=SKOS.altLabel,
                skosxl_predicate=SKOSXL.altLabel,
            )

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

    _LABEL_CLASS = Label

    @property
    def alt_label(self) -> Iterable[Label | Literal]:
        yield from self._values(SKOS.altLabel, self._map_term_to_literal)
        yield from self._values(
            SKOSXL.altLabel,
            lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
        )  # type: ignore

    @property
    def pref_label(self) -> Iterable[Label | Literal]:
        yield from self._values(SKOS.prefLabel, self._map_term_to_literal)
        yield from self._values(
            SKOSXL.prefLabel,
            lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
        )  # type: ignore
