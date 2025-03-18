import pytest
from graphs2go.namespaces import RDF, RDFS, SDO
from graphs2go.models import rdf
from rdflib import Graph


@pytest.fixture(scope="session")
def rdf_graphs(
    schema_rdf_graph: Graph,
    vocab_rdf_graph: Graph,
) -> tuple[Graph, ...]:
    return (schema_rdf_graph, vocab_rdf_graph)


@pytest.fixture(scope="session")
def schema_rdf_graph() -> Graph:
    graph = Graph(identifier=rdf.Iri("http://example.com/graph/schema"))
    graph.add((rdf.Iri("http://example.com/class"), RDF.type, RDFS.Class))
    return graph


@pytest.fixture(scope="session")
def vocab_rdf_graph() -> Graph:
    graph = Graph(identifier=rdf.Iri("http://example.com/graph/vocab"))
    graph.add(
        (rdf.Iri("http://example.com/instance"), SDO.name, rdf.Literal("Test instance"))
    )
    return graph
