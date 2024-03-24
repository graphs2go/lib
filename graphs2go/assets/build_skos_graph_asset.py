from urllib.parse import quote
from tqdm import tqdm

from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from rdflib import URIRef

from graphs2go.models import interchange, skos
from graphs2go.resources.rdf_store_config import RdfStoreConfig
from graphs2go.transformers.transform_interchange_graph_to_skos_models import (
    transform_interchange_graph_to_skos_models,
)


def build_skos_graph_asset(
    *, partitions_def: PartitionsDefinition | None = None
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def)
    def skos_graph(
        interchange_graph: interchange.Graph.Descriptor,
        rdf_store_config: RdfStoreConfig,
    ) -> skos.Graph.Descriptor:
        logger = get_dagster_logger()

        with interchange.Graph.open(
            interchange_graph, read_only=True
        ) as open_interchange_graph, skos.Graph.create(
            identifier=URIRef(f"urn:skos:{quote(interchange_graph.identifier)}"),
            rdf_store_config=rdf_store_config,
        ) as open_skos_graph:
            logger.info("loading SKOS graph")
            open_skos_graph.add_all(
                tqdm(
                    transform_interchange_graph_to_skos_models(open_interchange_graph),
                    desc="SKOS models",
                )
            )
            logger.info("loaded SKOS graph")
            return open_skos_graph.descriptor

    return skos_graph
