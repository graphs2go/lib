from __future__ import annotations
from dataclasses import dataclass
import logging
from pathlib import Path

import oxrdflib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pathvalidate import sanitize_filename
import pyoxigraph
from rdflib import ConjunctiveGraph, Graph, URIRef

from graphs2go.models.interchange.graph_descriptor import GraphDescriptor


if TYPE_CHECKING:
    from graphs2go.resources.oxigraph_config import OxigraphConfig
    from graphs2go.models.interchange.model import Model


logger = logging.getLogger(__name__)


class InterchangeGraphLoader(ABC):
    def __init__(self, *, interchange_graph_identifier: URIRef):
        self._interchange_graph_identifier = interchange_graph_identifier

    @abstractmethod
    def close(self) -> None:
        pass

    @staticmethod
    def create(
        *,
        interchange_graph_identifier: URIRef,
        oxigraph_config: OxigraphConfig,
    ) -> InterchangeGraphLoader:
        return _OxigraphInterchangeGraphLoader.create(
            interchange_graph_identifier=interchange_graph_identifier,
            oxigraph_config_parsed=oxigraph_config.parse(),
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @abstractmethod
    def load(self, *, model: Model) -> None:
        pass

    @property
    @abstractmethod
    def loaded(self) -> bool:
        """
        Is the graph already loaded?
        """

    @staticmethod
    def open(*, descriptor: GraphDescriptor) -> InterchangeGraphLoader:
        if isinstance(
            descriptor, _OxigraphInterchangeGraphLoader._Descriptor  # noqa: SLF001
        ):
            return _OxigraphInterchangeGraphLoader.open(descriptor=descriptor)
        raise TypeError(type(descriptor))

    @abstractmethod
    def reverse_load(self) -> Graph:
        """
        Get a single rdflib Graph of the loaded models.
        """


class _OxigraphInterchangeGraphLoader(InterchangeGraphLoader):
    @dataclass(frozen=True)
    class _Descriptor(GraphDescriptor):
        oxigraph_directory_path: Path

    def __init__(
        self,
        *,
        interchange_graph_identifier: URIRef,
        oxigraph_directory_path: Path,
    ):
        InterchangeGraphLoader.__init__(
            self,
            interchange_graph_identifier=interchange_graph_identifier,
        )
        self.__oxigraph_directory_path = oxigraph_directory_path
        self.__oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        self.__graph = ConjunctiveGraph(
            store=oxrdflib.OxigraphStore(
                store=pyoxigraph.Store(self.__oxigraph_directory_path)
            )
        )

    def close(self) -> None:
        self.__graph.close()

    @staticmethod
    def create(
        *,
        interchange_graph_identifier: URIRef,
        oxigraph_config_parsed: OxigraphConfig.Parsed,
    ) -> _OxigraphInterchangeGraphLoader:
        oxigraph_directory_path = (
            oxigraph_config_parsed.directory_path
            / "interchange"
            / sanitize_filename(interchange_graph_identifier)
        )
        oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        return _OxigraphInterchangeGraphLoader(
            interchange_graph_identifier=interchange_graph_identifier,
            oxigraph_directory_path=oxigraph_directory_path,
        )

    @property
    def descriptor(self) -> GraphDescriptor:
        return self._Descriptor(
            identifier=self._interchange_graph_identifier,
            oxigraph_directory_path=self.__oxigraph_directory_path,
        )

    def load(self, model: Model) -> None:
        self.__graph += model.resource.graph

    @property
    def loaded(self) -> bool:
        for _ in self.__graph.triples((None, None, None)):
            return True
        return False

    @staticmethod
    def open(*, descriptor: _Descriptor) -> _OxigraphInterchangeGraphLoader:
        return _OxigraphInterchangeGraphLoader(
            interchange_graph_identifier=descriptor.identifier,
            oxigraph_directory_path=descriptor.oxigraph_directory_path,
        )

    def reverse_load(self) -> Graph:
        return self.__graph
