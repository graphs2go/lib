from rdflib import Graph

from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.namespaces.snomed_schema import SNOMED_SCHEMA
from graphs2go.namespaces.snomed_vocab import SNOMED_VOCAB


def bind_namespaces(graph: Graph) -> None:
    graph.bind("interchange", INTERCHANGE)
    graph.bind("snomed-ct", SNOMED_VOCAB)
    graph.bind("snomed-cts", SNOMED_SCHEMA)
    graph.bind("skosxl", SKOSXL)
