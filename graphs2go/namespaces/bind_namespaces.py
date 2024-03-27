from rdflib import Graph

from graphs2go.namespaces.dash import DASH
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.namespaces.snomed_schema import SNOMED_SCHEMA
from graphs2go.namespaces.snomed_vocab import SNOMED_VOCAB
from graphs2go.namespaces.vaem import VAEM
from graphs2go.namespaces.voag import VOAG


def bind_namespaces(graph: Graph) -> None:
    graph.bind("dash", DASH)
    graph.bind("interchange", INTERCHANGE)
    graph.bind("snomedct", SNOMED_VOCAB)
    graph.bind("snomedcts", SNOMED_SCHEMA)
    graph.bind("skosxl", SKOSXL)
    graph.bind("vaem", VAEM)
    graph.bind("voag", VOAG)
