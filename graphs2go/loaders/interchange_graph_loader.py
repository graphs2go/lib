from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from rdflib import Graph, URIRef

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models.rdf_format import RdfFormat

if TYPE_CHECKING:
    from graphs2go.models.interchange.model import Model
    from graphs2go.resources.interchange_config import InterchangeConfig


class InterchangeGraphLoader(ABC):
    def __init__(
        self,
        *,
        interchange_config_parsed: InterchangeConfig.Parsed,
        interchange_graph_identifier: URIRef,
    ):
        self._interchange_config_parsed = interchange_config_parsed
        self._interchange_graph_identifier = interchange_graph_identifier

    @abstractmethod
    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @staticmethod
    def create(
        *, interchange_config: InterchangeConfig, interchange_graph_identifier: URIRef
    ) -> InterchangeGraphLoader:
        interchange_config_parsed = interchange_config.parse()
        return _NtriplesFileInterchangeGraphLoader(
            interchange_config_parsed=interchange_config_parsed,
            interchange_graph_identifier=interchange_graph_identifier,
        )

    @abstractmethod
    def load(self, *, model: Model) -> None:
        pass

    @property
    @abstractmethod
    def loaded(self) -> bool:
        """
        Is the graph already loaded?
        """

    @abstractmethod
    def reverse_load(self) -> Graph:
        """
        Get a single rdflib Graph of the loaded models.
        """


class _NtriplesFileInterchangeGraphLoader(InterchangeGraphLoader):
    def __init__(
        self,
        *,
        interchange_config_parsed: InterchangeConfig.Parsed,
        interchange_graph_identifier: URIRef,
    ):
        InterchangeGraphLoader.__init__(
            self,
            interchange_config_parsed=interchange_config_parsed,
            interchange_graph_identifier=interchange_graph_identifier,
        )
        self.__delegate = RdfDirectoryLoader.create(
            directory_path=interchange_config_parsed.directory_path,
            rdf_format=RdfFormat.NTRIPLES,
        )

    def close(self) -> None:
        self.__delegate.close()

    def load(self, model: Model) -> None:
        if model.resource.graph.identifier == self._interchange_graph_identifier:
            self.__delegate.load(model.resource.graph)
        else:
            graph = Graph(identifier=self._interchange_graph_identifier)
            graph += model.resource.graph
            self.__delegate.load(graph)

    @property
    def loaded(self) -> bool:
        return self.__delegate.rdf_graph_file_path(
            self._interchange_graph_identifier
        ).is_file()

    def reverse_load(self) -> Graph:
        graph = Graph(identifier=self._interchange_graph_identifier)
        graph.parse(
            self.__delegate.rdf_graph_file_path(self._interchange_graph_identifier)
        )
        return graph
