from collections.abc import Callable

from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from pathvalidate import sanitize_filename
from returns.maybe import Maybe, Nothing

from graphs2go.assets.rdf_file_asset_defaults import RDF_FILE_FORMATS_DEFAULT
from graphs2go.models import rdf
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.resources.output_config import OutputConfig
from graphs2go.stores.skos import ModelStore as SkosModelStore
from graphs2go.loaders.rdf import FileLoader as RdfFileLoader


def build_skos_file_asset(
    *,
    partitions_def: Maybe[PartitionsDefinition] = Nothing,
    rdf_file_formats: tuple[rdf.FileFormat, ...] = RDF_FILE_FORMATS_DEFAULT,
    rdf_namespace_prefixes: Maybe[rdf.NamespacePrefixes] = Nothing,
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def skos_file(
        output_config: OutputConfig, skos_model_store: SkosModelStore.Descriptor
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "skos"
        with SkosModelStore.open(
            skos_model_store, read_only=True
        ) as open_skos_model_store:
            for rdf_file_format in rdf_file_formats:
                output_file_path = (
                    output_directory_path
                    / sanitize_filename(open_skos_model_store.identifier.namespace)
                    / f"{sanitize_filename(open_skos_model_store.identifier.name)}{rdf_file_format.file_extension}"
                )
                logger.info("loading SKOS models to %s", output_file_path)
                with RdfFileLoader.create(
                    file_format=rdf_file_format,
                    file_path=output_file_path,
                    namespace_prefixes=rdf_namespace_prefixes,
                ) as loader:
                    loader.load(open_skos_model_store.quad_store)
            logger.info("loaded SKOS models to %s", output_file_path)

    return skos_file
