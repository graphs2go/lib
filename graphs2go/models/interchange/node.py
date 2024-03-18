from __future__ import annotations


from graphs2go.models.interchange.model import Model
from graphs2go.namespaces.interchange import INTERCHANGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rdflib import URIRef


class Node(Model):
    """
    Top-level node in the interchange graph, equivalent to a node in a labeled property graph.
    """

    @classmethod
    def builder(cls, *, uri: URIRef) -> Node.Builder:
        return cls.Builder(cls._create_resource(uri))

    @classmethod
    def rdf_type_uri(cls) -> URIRef:
        return INTERCHANGE.Node
