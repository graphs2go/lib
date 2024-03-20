from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import RDF

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

    @classmethod
    def builder(
        cls,
        *,
        literal_form: Literal,
        predicate: URIRef,
        subject: URIRef,
        uri: URIRef | None = None,
    ) -> Label.Builder:
        resource = cls._create_resource(uri if uri is not None else uuid_urn())
        resource.add(RDF.subject, subject)
        resource.add(RDF.predicate, predicate)
        resource.add(RDF.type, SKOSXL.Label)
        resource.add(SKOSXL.literalForm, literal_form)
        # Add direct statements for ease of querying
        for node_to_label_predicate in (predicate, INTERCHANGE.label):
            resource.graph.add((subject, node_to_label_predicate, resource.identifier))
        return cls.Builder(resource)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return INTERCHANGE.Label
