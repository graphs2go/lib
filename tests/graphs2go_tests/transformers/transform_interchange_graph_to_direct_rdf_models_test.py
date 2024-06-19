from rdflib import RDF, Graph, SKOS

from graphs2go.models import interchange, rdf
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.transformers.transform_interchange_graph_to_direct_rdf_models import (
    transform_interchange_graph_to_direct_rdf_models,
)


def test_transform(interchange_graph_descriptor: interchange.Graph.Descriptor) -> None:
    rdf_graph: rdf.Graph[rdf.NamedModel] = rdf.Graph(
        identifier=interchange_graph_descriptor.identifier, rdf_store=MemoryRdfStore()
    )
    rdf_graph.add_all(
        transform_interchange_graph_to_direct_rdf_models(interchange_graph_descriptor)
    )

    rdflib_graph: Graph = rdf_graph.rdflib_graph
    assert (
        len(tuple(rdflib_graph.subjects(predicate=RDF.type, object=SKOS.ConceptScheme)))
        == 1
    )
    assert (
        len(tuple(rdflib_graph.subjects(predicate=RDF.type, object=SKOS.Concept))) == 2
    )
