from abc import ABC, abstractmethod

from graphs2go.models.loadable_rdf_graph import LoadableRdfGraph


class RdfLoader(ABC):
    @abstractmethod
    def __call__(self, loadable_rdf_graph: LoadableRdfGraph) -> None:
        pass
