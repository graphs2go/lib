from abc import ABC, abstractmethod
from rdflib import Graph


class RdfLoader(ABC):
    @abstractmethod
    def __call__(self, rdf_graph: Graph) -> None:
        pass
