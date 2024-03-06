from abc import ABC, abstractmethod

from graphs2go.models.rdf_graph_record import RdfGraphRecord


class RdfLoader(ABC):
    @abstractmethod
    def __call__(self, rdf_graph_record: RdfGraphRecord) -> None:
        pass
