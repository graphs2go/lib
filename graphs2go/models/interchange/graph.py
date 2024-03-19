from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathvalidate import sanitize_filename
import rdflib

from graphs2go.models.interchange.node import Node
from graphs2go.namespaces.interchange import INTERCHANGE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphs2go.resources.oxigraph_config import OxigraphConfig
    from graphs2go.models.interchange.model import Model
    from pathlib import Path
    from collections.abc import Iterable


class Graph(ABC):
    """
    Non-picklable interchange graph. Used as an entry point for accessing top-level graph models.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an interchange graph. It can be used to open an InterchangeGraph.
        """

    def __init__(self, *, rdf_graph: rdflib.Graph):
        self.__rdf_graph = rdf_graph

    def add(self, model: Model) -> None:
        self.__rdf_graph += model.resource.graph

    @staticmethod
    def create(
        *,
        identifier: rdflib.URIRef,
        oxigraph_config: OxigraphConfig,
    ) -> Graph:
        return _OxigraphGraph.create(
            identifier=identifier,
            oxigraph_config_parsed=oxigraph_config.parse(),
        )

    @property
    @abstractmethod
    def descriptor(self) -> Descriptor:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.__rdf_graph.close()

    @property
    def is_empty(self) -> bool:
        for _ in self.__rdf_graph.triples((None, None, None)):
            return False
        return True

    @property
    def nodes(self) -> Iterable[Node]:
        for subject_uri in self.__rdf_graph.subjects(
            predicate=rdflib.RDF.type, object=INTERCHANGE.Node
        ):
            yield Node(resource=self.__rdf_graph.resource(subject_uri))

    @staticmethod
    def open(*, descriptor: Descriptor) -> Graph:
        if isinstance(descriptor, _OxigraphGraph.Descriptor):
            return _OxigraphGraph.open(descriptor=descriptor)
        raise TypeError(type(descriptor))


class _OxigraphGraph(Graph):
    @dataclass(frozen=True)
    class Descriptor(Graph.Descriptor):
        oxigraph_directory_path: Path

    def __init__(
        self,
        *,
        oxigraph_directory_path: Path,
    ):
        import oxrdflib
        import pyoxigraph

        Graph.__init__(
            self,
            rdf_graph=rdflib.ConjunctiveGraph(
                store=oxrdflib.OxigraphStore(
                    store=pyoxigraph.Store(oxigraph_directory_path)
                )
            ),
        )
        self.__oxigraph_directory_path = oxigraph_directory_path

    @staticmethod
    def create(
        *,
        identifier: rdflib.URIRef,
        oxigraph_config_parsed: OxigraphConfig.Parsed,
    ) -> _OxigraphGraph:
        oxigraph_directory_path = (
            oxigraph_config_parsed.directory_path
            / "interchange"
            / sanitize_filename(identifier)
        )
        oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        return _OxigraphGraph(
            oxigraph_directory_path=oxigraph_directory_path,
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            oxigraph_directory_path=self.__oxigraph_directory_path,
        )

    @staticmethod
    def open(*, descriptor: Descriptor) -> _OxigraphGraph:
        return _OxigraphGraph(
            oxigraph_directory_path=descriptor.oxigraph_directory_path,
        )
