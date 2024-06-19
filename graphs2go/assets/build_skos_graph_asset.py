from urllib.parse import quote

from dagster import AssetsDefinition, PartitionsDefinition, asset
from rdflib import URIRef
from returns.maybe import Maybe, Nothing
from tqdm import tqdm

from graphs2go.models import interchange, skos
from graphs2go.resources.rdf_store_config import RdfStoreConfig
from graphs2go.transformers.transform_interchange_graph_to_skos_models import (
    transform_interchange_graph_to_skos_models,
)


def build_skos_graph_asset(
    *, partitions_def: Maybe[PartitionsDefinition] = Nothing
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def skos_graph(
        interchange_graph: interchange.Graph.Descriptor,
        rdf_store_config: RdfStoreConfig,
    ) -> skos.Graph.Descriptor:
        with skos.Graph.create(
            identifier=URIRef(f"urn:skos:{quote(interchange_graph.identifier)}"),
            rdf_store_config=rdf_store_config,
        ) as open_skos_graph:
            return open_skos_graph.add_all_if_empty(
                lambda: tqdm(
                    transform_interchange_graph_to_skos_models(interchange_graph),
                    desc="SKOS graph models",
                )
            ).descriptor

    return skos_graph
