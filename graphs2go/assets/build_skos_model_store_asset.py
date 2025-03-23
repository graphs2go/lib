from urllib.parse import quote

from dagster import AssetsDefinition, PartitionsDefinition, asset
from returns.maybe import Maybe, Nothing
from tqdm import tqdm

from graphs2go.models import rdf
from graphs2go.resources.rdf_store_config import RdfStoreConfig
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.stores.skos import ModelStore as SkosModelStore
from graphs2go.transformers.transform_interchange_models_to_skos_models import (
    transform_interchange_models_to_skos_models,
)


def build_skos_model_store_asset(
    *, partitions_def: Maybe[PartitionsDefinition] = Nothing
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def skos_model_store(
        interchange_model_store: InterchangeModelStore.Descriptor,
        rdf_store_config: RdfStoreConfig,
    ) -> SkosModelStore.Descriptor:
        with SkosModelStore.create(
            identifier=rdf.Iri(f"urn:skos:{quote(interchange_model_store.identifier)}"),
            quad_store_config=rdf_store_config,
        ) as open_skos_model_store:
            return open_skos_model_store.extend_if_empty(
                lambda: tqdm(
                    transform_interchange_models_to_skos_models(
                        interchange_model_store
                    ),
                    desc="SKOS graph models",
                )
            ).descriptor

    return skos_model_store
