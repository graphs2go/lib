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

    # def interchange_dataset(interchange_config: InterchangeConfig) -> Dataset:
    #     dataset_file_path = loader.rdf_graph_file_path(interchange_dataset_identifier)
    #     logger = get_dagster_logger()

    #     if dataset_file_path.is_file():
    #         if interchange_config_parsed.recreate:
    #             logger.info(
    #                 "interchange dataset %s already exists but recreate specified, deleting",
    #                 dataset_file_path,
    #             )
    #             dataset_file_path.unlink()
    #         else:
    #             logger.info(
    #                 "interchange dataset %s already exists, skipping build",
    #                 dataset_file_path,
    #             )
    #             return Dataset(
    #                 identifier=interchange_dataset_identifier,
    #             )

    #     for interchange_model in interchange_models:
    #         # Always load conjunctive graph with the dataset identifier so that everything ends up in the same place
    #         conjunctive_graph = ConjunctiveGraph(
    #             identifier=interchange_dataset_identifier
    #         )

    #         # Copy the model graph to the conjunctive graph
    #         if isinstance(interchange_model.resource.graph.identifier, BNode):
    #             # No explicit graph identifier = dump the triples into the conjunctive graph's default graph
    #             graph = conjunctive_graph.default_context
    #         else:
    #             # Else put the triples into the right named graph on the conjunctive graph
    #             # A model can't be spread across multiple named graphs
    #             graph = conjunctive_graph.get_context(
    #                 interchange_model.resource.graph.identifier
    #             )
    #         graph += interchange_model.resource.graph

    #         loader.load(graph)

    #     return Dataset(identifier=interchange_dataset_identifier)

    # return interchange_dataset
