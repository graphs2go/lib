import pytest
from rdflib import RDF, RDFS, SDO, Graph, Literal, URIRef

from loaders.rdf_graph_record import RdfGraphRecord


@pytest.fixture(scope="session")
def rdf_graph_records(
    schema_rdf_graph_record: RdfGraphRecord, vocab_rdf_graph_record: RdfGraphRecord
) -> tuple[RdfGraphRecord, ...]:
    return (schema_rdf_graph_record, vocab_rdf_graph_record)


@pytest.fixture(scope="session")
def schema_rdf_graph_record() -> RdfGraphRecord:
    graph = Graph()
    graph.add((URIRef("http://example.com/class"), RDF.type, RDFS.Class))
    return RdfGraphRecord(stream="schema", graph=graph)


@pytest.fixture(scope="session")
def vocab_rdf_graph_record() -> RdfGraphRecord:
    graph = Graph()
    graph.add(
        (URIRef("http://example.com/instance"), SDO.name, Literal("Test instance"))
    )
    return RdfGraphRecord(stream="vocab", graph=graph)
