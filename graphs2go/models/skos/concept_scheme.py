from rdflib import SKOS, URIRef
from graphs2go.models.skos.model import Model


class ConceptScheme(Model):
    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return SKOS.ConceptScheme
