from urllib.parse import quote

from dagster import AssetsDefinition, PartitionsDefinition, asset
from rdflib import URIRef
from returns.maybe import Maybe, Nothing
from tqdm import tqdm

from graphs2go.models import interchange, rdf
from graphs2go.resources import RdfStoreConfig
from graphs2go.transformers import transform_interchange_graph_to_direct_rdf_models


def build_direct_rdf_graph_asset(
    *, partitions_def: Maybe[PartitionsDefinition] = Nothing
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def direct_rdf_graph(
        interchange_graph: interchange.Graph.Descriptor,
        rdf_store_config: RdfStoreConfig,
    ) -> rdf.Graph.Descriptor:
        with rdf.Graph.create(
            identifier=URIRef(f"urn:direct_rdf:{quote(interchange_graph.identifier)}"),
            rdf_store_config=rdf_store_config,
        ) as open_rdf_graph:
            return open_rdf_graph.add_all_if_empty(
                lambda: tqdm(
                    transform_interchange_graph_to_direct_rdf_models(interchange_graph),
                    desc="Direct RDF graph models",
                )
            ).descriptor

    return direct_rdf_graph
