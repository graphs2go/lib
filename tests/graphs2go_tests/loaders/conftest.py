import pytest
from rdflib import RDF, RDFS, SDO, Graph, Literal, URIRef

from graphs2go.models.loadable_rdf_graph import LoadableRdfGraph


@pytest.fixture(scope="session")
def loadable_rdf_graphs(
    schema_loadable_rdf_graph: LoadableRdfGraph,
    vocab_loadable_rdf_graph: LoadableRdfGraph,
) -> tuple[LoadableRdfGraph, ...]:
    return (schema_loadable_rdf_graph, vocab_loadable_rdf_graph)


@pytest.fixture(scope="session")
def schema_loadable_rdf_graph() -> LoadableRdfGraph:
    graph = Graph()
    graph.add((URIRef("http://example.com/class"), RDF.type, RDFS.Class))
    return LoadableRdfGraph(stream="schema", graph=graph)


@pytest.fixture(scope="session")
def vocab_loadable_rdf_graph() -> LoadableRdfGraph:
    graph = Graph()
    graph.add(
        (URIRef("http://example.com/instance"), SDO.name, Literal("Test instance"))
    )
    return LoadableRdfGraph(stream="vocab", graph=graph)
