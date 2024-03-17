import pytest
from rdflib import RDF, RDFS, SDO, Graph, Literal, URIRef


@pytest.fixture(scope="session")
def rdf_graphs(
    schema_rdf_graph: Graph,
    vocab_rdf_graph: Graph,
) -> tuple[Graph, ...]:
    return (schema_rdf_graph, vocab_rdf_graph)


@pytest.fixture(scope="session")
def schema_rdf_graph() -> Graph:
    graph = Graph(URIRef("http://example.com/graph/schema"))
    graph.add((URIRef("http://example.com/class"), RDF.type, RDFS.Class))
    return graph


@pytest.fixture(scope="session")
def vocab_rdf_graph() -> Graph:
    graph = Graph(URIRef("http://example.com/graph/vocab"))
    graph.add(
        (URIRef("http://example.com/instance"), SDO.name, Literal("Test instance"))
    )
    return graph
