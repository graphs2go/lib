from collections.abc import Iterable
import rdflib

from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE


class Graph:
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    def __init__(self, *, rdf_graph: rdflib.Graph):
        self.__rdf_graph = rdf_graph

    @property
    def nodes(self) -> Iterable[Node]:
        for subject_uri in self.__rdf_graph.subjects(
            predicate=rdflib.RDF.type, object=INTERCHANGE.Node
        ):
            yield Node(resource=self.__rdf_graph.resource(subject_uri))
