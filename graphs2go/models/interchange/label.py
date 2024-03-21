from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import RDF, RDFS, SKOS

from enum import Enum
from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.utils.uuid_urn import uuid_urn

if TYPE_CHECKING:
    from rdflib import Literal, URIRef


class Label(Model):
    """
    A label for a Node in the interchange graph.
    """

    class Builder(Model.Builder):
        def build(self) -> Label:
            return Label(resource=self._resource)

    class Type(Enum):
        ALTERNATIVE = 1
        PREFERRED = 2

    @classmethod
    def builder(
        cls,
        *,
        literal_form: Literal,
        subject: URIRef,
        type_: Type | None = None,
        uri: URIRef | None = None,
    ) -> Label.Builder:
        if type_ == Label.Type.ALTERNATIVE:
            skos_predicate = SKOS.altLabel
            skosxl_predicate = SKOSXL.altLabel
        elif type_ == Label.Type.PREFERRED:
            skos_predicate = SKOS.prefLabel
            skosxl_predicate = SKOSXL.prefLabel
        else:
            skos_predicate = RDFS.label
            skosxl_predicate = None

        resource = cls._create_resource(uri if uri is not None else uuid_urn())
        resource.add(RDF.predicate, skos_predicate)
        resource.add(RDF.subject, subject)
        resource.add(RDF.type, SKOSXL.Label)
        resource.add(SKOSXL.literalForm, literal_form)

        # Add direct statements for ease of querying
        resource.graph.add((subject, INTERCHANGE.label, resource.identifier))
        if skosxl_predicate is not None:
            resource.graph.add((subject, skosxl_predicate, resource.identifier))

        return cls.Builder(resource)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return INTERCHANGE.Label
