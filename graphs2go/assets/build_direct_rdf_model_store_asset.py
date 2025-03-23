from urllib.parse import quote

from dagster import AssetsDefinition, PartitionsDefinition, asset
from returns.maybe import Maybe, Nothing
from tqdm import tqdm

from graphs2go.models import rdf
from graphs2go.resources import RdfStoreConfig
from graphs2go.transformers import transform_interchange_models_to_direct_rdf_models
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.stores.rdf import ModelStore as RdfModelStore


def build_direct_rdf_graph_asset(
    *, partitions_def: Maybe[PartitionsDefinition] = Nothing
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def direct_rdf_graph(
        interchange_model_store: InterchangeModelStore.Descriptor,
        rdf_store_config: RdfStoreConfig,
    ) -> RdfModelStore.Descriptor:
        with RdfModelStore.create(
            config=rdf_store_config,
            identifier=rdf.Iri(
                f"urn:direct_rdf:{quote(interchange_model_store.identifier)}"
            ),
        ) as open_rdf_graph:
            return open_rdf_graph.extend_if_empty(
                lambda: tqdm(
                    transform_interchange_models_to_direct_rdf_models(
                        interchange_model_store
                    ),
                    desc="Direct RDF graph models",
                )
            ).descriptor

    return direct_rdf_graph
