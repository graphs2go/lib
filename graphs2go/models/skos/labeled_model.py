from collections.abc import Iterable
from typing import Self

from rdflib import Literal, URIRef

from graphs2go.models.label_type import LabelType
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model


class LabeledModel(Model):
    class Builder(Model.Builder):
        def add_lexical_label(
            self, *, label: Label | Literal | URIRef, type_: LabelType
        ) -> Self:
            if isinstance(label, Label):
                self._resource.add(type_.skosxl_predicate, label.iri)
            elif isinstance(label, Literal):
                self._resource.add(type_.skos_predicate, label)
            elif isinstance(label, URIRef):
                self._resource.add(type_.skosxl_predicate, label)
            else:
                raise TypeError(type(label))
            return self

    _LABEL_CLASS = Label

    @property
    def lexical_labels(self) -> Iterable[tuple[LabelType, Label | Literal]]:
        for label_type in LabelType:
            for literal in self._values(
                label_type.skos_predicate, self._map_term_to_literal
            ):
                yield label_type, literal

            for model in self._values(
                label_type.skosxl_predicate,
                lambda term: self._map_term_to_model(self._LABEL_CLASS, term),
            ):  # type: ignore
                yield label_type, model
