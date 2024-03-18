from rdflib import Literal, URIRef

from graphs2go.models.skos.model import Model
from graphs2go.namespaces.skosxl import SKOSXL


class Label(Model):
    @property
    def literal_form(self) -> Literal:
        return self._required_value(SKOSXL.literalForm, self._map_term_to_literal)

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return SKOSXL.Label
