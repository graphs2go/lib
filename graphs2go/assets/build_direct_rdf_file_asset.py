from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from returns.maybe import Maybe, Nothing

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import rdf
from graphs2go.namespaces import SDO
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.resources.output_config import OutputConfig


def build_direct_rdf_file_asset(
    *,
    partitions_def: Maybe[PartitionsDefinition] = Nothing,
    rdf_formats: tuple[rdf.Format, ...] = (rdf.Format.NQUADS,)
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def direct_rdf_file(
        output_config: OutputConfig, direct_rdf_graph: rdf.Graph.Descriptor
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "direct_rdf"
        for rdf_format in rdf_formats:
            logger.info(
                "loading direct RDF graph to %s files in %s",
                rdf_format.file_extension,
                output_directory_path,
            )
            with RdfDirectoryLoader.create(
                directory_path=output_directory_path,
                rdf_format=rdf_format,
            ) as loader, rdf.Graph.open(
                direct_rdf_graph, read_only=True
            ) as open_rdf_graph:
                rdflib_graph = open_rdf_graph.rdflib_graph
                rdflib_graph.bind("schema", SDO)
                rdflib_graph.bind("skosxl", SKOSXL)
                loader.load(rdflib_graph)
            logger.info(
                "loaded direct RDF graph to %s files in %s",
                rdf_format.file_extension,
                output_directory_path,
            )

    return direct_rdf_file
