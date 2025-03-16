from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from rdflib import Namespace
from rdflib.namespace import DefinedNamespace
from returns.maybe import Maybe, Nothing

from graphs2go.assets.rdf_file_asset_defaults import RDF_FILE_FORMATS_DEFAULT
from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import interchange, rdf
from graphs2go.namespaces import NAMESPACES
from graphs2go.resources.output_config import OutputConfig


def build_interchange_file_asset(
    *,
    partitions_def: Maybe[PartitionsDefinition] = Nothing,
    namespaces: dict[str, type[DefinedNamespace] | Namespace] = NAMESPACES,
    rdf_file_formats: tuple[rdf.FileFormat, ...] = RDF_FILE_FORMATS_DEFAULT,
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def interchange_file(
        output_config: OutputConfig, interchange_graph: interchange.Graph.Descriptor
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "interchange"
        for rdf_file_format in rdf_file_formats:
            logger.info(
                "loading interchange graph to %s files in %s",
                rdf_file_format.format_.file_extension,
                output_directory_path,
            )
            with (
                RdfDirectoryLoader.create(
                    directory_path=output_directory_path,
                    rdf_file_format=rdf_file_format,
                ) as loader,
                interchange.Graph.open(
                    interchange_graph, read_only=True
                ) as open_interchange_graph,
            ):
                rdflib_graph = open_interchange_graph.rdflib_graph
                for namespace_prefix, namespace in namespaces.items():
                    rdflib_graph.bind(namespace_prefix, namespace)
                loader.load(rdflib_graph)
            logger.info(
                "loaded interchange graph to %s files in %s",
                rdf_file_format.format_.file_extension,
                output_directory_path,
            )

    return interchange_file
