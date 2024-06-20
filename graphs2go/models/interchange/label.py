from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rdflib import RDF, RDFS
from returns.maybe import Maybe, Nothing

from graphs2go.models import rdf
from graphs2go.models.interchange.model import Model
from graphs2go.models.label_type import LabelType
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.utils.uuid_urn import uuid_urn

if TYPE_CHECKING:
    from rdflib import Literal, URIRef


class Label(Model):
    """
    A human-readable label for a Node in the interchange graph.
    """

    class Builder(Model.Builder):
        def build(self) -> Label:
            return Label(self._resource_builder.build())

    __TYPE_TO_PREDICATE_MAP: ClassVar[dict[LabelType | None, URIRef]] = {
        label_type: label_type.skos_predicate for label_type in LabelType
    }
    __TYPE_TO_PREDICATE_MAP[None] = RDFS.label

    __PREDICATE_TO_TYPE_MAP: ClassVar[dict[URIRef, LabelType | None]] = {
        value: key for key, value in __TYPE_TO_PREDICATE_MAP.items()
    }

    @classmethod
    def builder(
        cls,
        *,
        literal_form: Literal,
        subject: rdf.NamedModel | URIRef,
        type_: Maybe[LabelType] = Nothing,
        iri: Maybe[URIRef] = Nothing,
    ) -> Label.Builder:
        resource_builder = rdf.NamedResource.builder(iri=iri.or_else_call(uuid_urn))
        resource_builder.add(
            RDF.predicate, cls.__TYPE_TO_PREDICATE_MAP[type_.value_or(None)]
        )
        subject_iri = subject.iri if isinstance(subject, rdf.NamedModel) else subject
        resource_builder.add(RDF.subject, subject_iri)
        resource_builder.add(RDF.type, INTERCHANGE.Label)
        resource_builder.add(RDF.type, SKOSXL.Label)
        resource_builder.add(SKOSXL.literalForm, literal_form)

        # Add direct statements for ease of querying
        resource_builder.graph.add(
            (subject_iri, INTERCHANGE.label, resource_builder.identifier)
        )
        # if type_ is not None:
        #     resource.graph.add(
        #         (subject_iri, type_.skosxl_predicate, resource.identifier)
        #     )

        return cls.Builder(resource_builder)

    @property
    def literal_form(self) -> Literal:
        return self.resource.required_value(
            SKOSXL.literalForm, rdf.Resource.ValueMappers.literal
        )

    @property
    def type(self) -> Maybe[LabelType]:
        return Maybe.from_optional(
            self.__PREDICATE_TO_TYPE_MAP[
                self.resource.required_value(
                    RDF.predicate, rdf.Resource.ValueMappers.iri
                )
            ]
        )
