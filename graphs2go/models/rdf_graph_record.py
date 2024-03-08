from dataclasses import dataclass

from rdflib import Graph

from graphs2go.models.record import Record


@dataclass(frozen=True)
class RdfGraphRecord(Record):
    graph: Graph
