from dataclasses import dataclass

import rdflib
from rdflib import URIRef

from graphs2go.loaders.interchange_graph_loader import InterchangeGraphLoader
from graphs2go.resources.interchange_config import InterchangeConfig


@dataclass(frozen=True)
class Graph:
    identifier: URIRef

    def to_rdflib_graph(self, interchange_config: InterchangeConfig) -> rdflib.Graph:
        return InterchangeGraphLoader.create(
            interchange_config=interchange_config,
            interchange_graph_identifier=self.identifier,
        ).reverse_load()
