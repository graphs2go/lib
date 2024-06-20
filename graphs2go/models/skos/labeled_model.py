from abc import ABC
from collections.abc import Iterable
from typing import Self

from rdflib import Literal, URIRef

from graphs2go.models import rdf
from graphs2go.models.label_type import LabelType
from graphs2go.models.skos.label import Label
from graphs2go.models.skos.model import Model


class LabeledModel(Model, ABC):
    class Builder(Model.Builder, ABC):
        def add_lexical_label(
            self, *, label: Label | Literal | URIRef, type_: LabelType
        ) -> Self:
            if isinstance(label, Label):
                self._resource_builder.add(type_.skosxl_predicate, label.iri)
            elif isinstance(label, Literal):
                self._resource_builder.add(type_.skos_predicate, label)
            elif isinstance(label, URIRef):
                self._resource_builder.add(type_.skosxl_predicate, label)
            else:
                raise TypeError(type(label))
            return self

    _LABEL_CLASS = Label

    def lexical_labels(self) -> Iterable[tuple[LabelType, Label | Literal]]:
        for label_type in LabelType:
            literal: Literal
            for literal in self.resource.values(
                label_type.skos_predicate, rdf.Resource.ValueMappers.literal
            ):
                yield label_type, literal

            resource: rdf.NamedResource
            for resource in self.resource.values(
                label_type.skosxl_predicate, rdf.Resource.ValueMappers.named_resource
            ):  # type: ignore
                yield label_type, self._LABEL_CLASS(resource)
