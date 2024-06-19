from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from returns.maybe import Nothing, Maybe

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import rdf, skos
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.resources.output_config import OutputConfig


def build_skos_file_asset(
    *,
    partitions_def: Maybe[PartitionsDefinition] = Nothing,
    rdf_formats: tuple[rdf.Format, ...] = (rdf.Format.NQUADS,)
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def skos_file(
        output_config: OutputConfig, skos_graph: skos.Graph.Descriptor
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "skos"
        for rdf_format in rdf_formats:
            logger.info(
                "loading SKOS graph to %s files in %s",
                rdf_format.file_extension,
                output_directory_path,
            )
            with RdfDirectoryLoader.create(
                directory_path=output_directory_path,
                rdf_format=rdf_format,
            ) as loader, skos.Graph.open(skos_graph, read_only=True) as open_skos_graph:
                rdflib_graph = open_skos_graph.rdflib_graph
                rdflib_graph.bind("skosxl", SKOSXL)
                loader.load(rdflib_graph)
            logger.info(
                "loaded SKOS graph to %s files in %s",
                rdf_format.file_extension,
                output_directory_path,
            )

    return skos_file
