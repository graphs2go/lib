from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from rdflib import Namespace
from rdflib.namespace import DefinedNamespace

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import interchange, rdf
from graphs2go.namespaces import NAMESPACES
from graphs2go.resources.output_config import OutputConfig


def build_interchange_file_asset(
    *,
    partitions_def: PartitionsDefinition | None = None,
    namespaces: dict[str, type[DefinedNamespace] | Namespace] = NAMESPACES,
    rdf_formats: tuple[rdf.Format, ...] = (rdf.Format.NQUADS,)
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def)
    def interchange_file(
        output_config: OutputConfig, interchange_graph: interchange.Graph.Descriptor
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "interchange"
        for rdf_format in rdf_formats:
            logger.info(
                "loading interchange graph to %s files in %s",
                rdf_format.file_extension,
                output_directory_path,
            )
            with RdfDirectoryLoader.create(
                directory_path=output_directory_path,
                rdf_format=rdf_format,
            ) as loader, interchange.Graph.open(
                interchange_graph, read_only=True
            ) as open_interchange_graph:
                rdflib_graph = open_interchange_graph.rdflib_graph
                for namespace_prefix, namespace in namespaces.items():
                    rdflib_graph.bind(namespace_prefix, namespace)
                loader.load(rdflib_graph)
            logger.info(
                "loaded interchange graph to %s files in %s",
                rdf_format.file_extension,
                output_directory_path,
            )

    return interchange_file
