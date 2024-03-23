from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, ClassVar

from rdflib import RDF, RDFS, SKOS

from graphs2go.models import rdf
from graphs2go.models.interchange.model import Model
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

    class Type(Enum):
        ALTERNATIVE = 1
        PREFERRED = 2

    __TYPE_TO_PREDICATE_MAP: ClassVar[dict[Type | None, URIRef]] = {
        Type.ALTERNATIVE: SKOS.altLabel,
        Type.PREFERRED: SKOS.prefLabel,
        None: RDFS.label,
    }

    __PREDICATE_TO_TYPE_MAP: ClassVar[dict[URIRef, Type | None]] = {
        value: key for key, value in __TYPE_TO_PREDICATE_MAP.items()
    }

    @classmethod
    def builder(
        cls,
        *,
        literal_form: Literal,
        subject: rdf.Model | URIRef,
        type_: Type | None = None,
        uri: URIRef | None = None,
    ) -> Label.Builder:
        skos_predicate = cls.__TYPE_TO_PREDICATE_MAP[type_]
        if skos_predicate == SKOS.altLabel:
            skosxl_predicate = SKOSXL.altLabel
        elif skos_predicate == SKOS.prefLabel:
            skosxl_predicate = SKOSXL.prefLabel
        else:
            skosxl_predicate = None

        resource = cls._create_resource(uri if uri is not None else uuid_urn())
        resource.add(RDF.predicate, skos_predicate)
        subject_uri = subject.uri if isinstance(subject, rdf.Model) else subject
        resource.add(RDF.subject, subject_uri)
        resource.add(RDF.type, SKOSXL.Label)
        resource.add(SKOSXL.literalForm, literal_form)

        # Add direct statements for ease of querying
        resource.graph.add((subject_uri, INTERCHANGE.label, resource.identifier))
        if skosxl_predicate is not None:
            resource.graph.add((subject_uri, skosxl_predicate, resource.identifier))

        return cls.Builder(resource)

    @property
    def literal_form(self) -> Literal:
        return self._required_value(SKOSXL.literalForm, self._map_term_to_literal)

    @classmethod
    def primary_rdf_type(cls) -> URIRef:
        return INTERCHANGE.Label

    @property
    def type(self) -> Type | None:
        return self.__PREDICATE_TO_TYPE_MAP[
            self._required_value(RDF.predicate, self._map_term_to_uri)
        ]
