from abc import ABC
from collections.abc import Iterable
from typing import Self

from graphs2go.models import rdf
from graphs2go.models.label_type import LabelType
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model
from graphs2go.utils import success_values


class Resource(Model, ABC):
    """
    Abstract base class of SKOS Concept and ConceptScheme.
    """

    class Builder(Model.Builder, ABC):
        def add_lexical_label(
            self, *, label: Label | rdf.Literal | rdf.Iri, type_: LabelType
        ) -> Self:
            if isinstance(label, Label):
                self._resource_builder.add(type_.skosxl_predicate, label.iri)
            elif isinstance(label, rdf.Literal):
                self._resource_builder.add(type_.skos_predicate, label)
            elif isinstance(label, rdf.Iri):
                self._resource_builder.add(type_.skosxl_predicate, label)
            else:
                raise TypeError(type(label))
            return self

    _LABEL_CLASS = Label

    def lexical_labels(self) -> Iterable[tuple[LabelType, Label | rdf.Literal]]:
        for label_type in LabelType:
            for literal in success_values(
                value.to_literal()
                for value in self.resource.values(label_type.skos_predicate)
            ):
                yield label_type, literal

            for resource in success_values(
                value.to_named_resource()
                for value in self.resource.values(label_type.skosxl_predicate)
            ):
                yield label_type, self._LABEL_CLASS(resource)
