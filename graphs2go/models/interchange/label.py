from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rdflib import RDF, RDFS

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
            return Label(resource=self._resource)

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
        subject: rdf.Model | URIRef,
        type_: LabelType | None = None,
        uri: URIRef | None = None,
    ) -> Label.Builder:
        resource = cls._create_resource(uri if uri is not None else uuid_urn())
        resource.add(RDF.predicate, cls.__TYPE_TO_PREDICATE_MAP[type_])
        subject_uri = subject.uri if isinstance(subject, rdf.Model) else subject
        resource.add(RDF.subject, subject_uri)
        resource.add(RDF.type, SKOSXL.Label)
        resource.add(SKOSXL.literalForm, literal_form)

        # Add direct statements for ease of querying
        resource.graph.add((subject_uri, INTERCHANGE.label, resource.identifier))
        if type_ is not None:
            resource.graph.add(
                (subject_uri, type_.skosxl_predicate, resource.identifier)
            )

        return cls.Builder(resource)

    @property
    def literal_form(self) -> Literal:
        return self._required_value(SKOSXL.literalForm, self._map_term_to_literal)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return INTERCHANGE.Label

    @property
    def type(self) -> LabelType | None:
        return self.__PREDICATE_TO_TYPE_MAP[
            self._required_value(RDF.predicate, self._map_term_to_uri)
        ]
