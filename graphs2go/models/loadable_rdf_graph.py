from dataclasses import dataclass

from rdflib import Graph


@dataclass(frozen=True)
class LoadableRdfGraph:
    graph: Graph
    stream: str
