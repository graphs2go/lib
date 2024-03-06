from dataclasses import dataclass
from rdflib import Graph

from loaders.record import Record


@dataclass(frozen=True)
class RdfGraphRecord(Record):
    graph: Graph
