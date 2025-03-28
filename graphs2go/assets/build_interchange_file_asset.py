from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from pathvalidate import sanitize_filename
from returns.maybe import Maybe, Nothing

from graphs2go.assets.rdf_file_asset_defaults import RDF_FILE_FORMATS_DEFAULT
from graphs2go.models import rdf
from graphs2go.resources.output_config import OutputConfig
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.loaders.rdf import FileLoader as RdfFileLoader


def build_interchange_file_asset(
    *,
    partitions_def: Maybe[PartitionsDefinition] = Nothing,
    rdf_file_formats: tuple[rdf.FileFormat, ...] = RDF_FILE_FORMATS_DEFAULT,
    rdf_namespace_prefixes: Maybe[rdf.NamespacePrefixes] = Nothing,
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def interchange_file(
        output_config: OutputConfig,
        interchange_model_store: InterchangeModelStore.Descriptor,
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "interchange"
        with InterchangeModelStore.open(
            interchange_model_store, read_only=True
        ) as open_interchange_model_store:
            for rdf_file_format in rdf_file_formats:
                output_file_path = (
                    output_directory_path
                    / sanitize_filename(interchange_model_store.identifier.namespace)
                    / f"{sanitize_filename(interchange_model_store.identifier.name)}{rdf_file_format.file_extension}"
                )

                logger.info("loading interchange models to %s", output_file_path)
                with RdfFileLoader.create(
                    file_format=rdf_file_format,
                    file_path=output_file_path,
                    namespace_prefixes=rdf_namespace_prefixes,
                ) as loader:
                    loader.load(open_interchange_model_store.quad_store)
                logger.info("loaded interchange models to %s", output_file_path)

    return interchange_file
