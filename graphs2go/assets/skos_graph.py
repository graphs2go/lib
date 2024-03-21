from dagster import asset

from graphs2go.models import interchange, skos
from graphs2go.resources.rdf_store_config import RdfStoreConfig
from graphs2go.transformers.transform_interchange_graph_to_skos_models import (
    transform_interchange_graph_to_skos_models,
)


@asset(code_version="1")
def skos_graph(
    interchange_graph: interchange.Graph.Descriptor, rdf_store_config: RdfStoreConfig
) -> skos.Graph.Descriptor:
    with interchange.Graph.open(
        interchange_graph
    ) as open_interchange_graph, skos.Graph.create(
        identifier=interchange_graph.identifier, rdf_store_config=rdf_store_config
    ) as open_skos_graph:
        open_skos_graph.add_all(
            transform_interchange_graph_to_skos_models(open_interchange_graph)
        )
        return open_skos_graph.descriptor
