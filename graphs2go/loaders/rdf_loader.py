from abc import ABC, abstractmethod

from rdflib import Graph


class RdfLoader(ABC):
    @abstractmethod
    def load(self, rdf_graph: Graph) -> None:
        pass
