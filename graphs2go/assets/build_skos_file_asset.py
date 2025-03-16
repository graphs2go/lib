from collections.abc import Callable

from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from rdflib import URIRef
from returns.maybe import Maybe, Nothing

from graphs2go.assets.rdf_file_asset_defaults import RDF_FILE_FORMATS_DEFAULT
from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import rdf, skos
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.resources.output_config import OutputConfig


def build_skos_file_asset(
    *,
    partitions_def: Maybe[PartitionsDefinition] = Nothing,
    rdf_file_formats: tuple[rdf.FileFormat, ...] = RDF_FILE_FORMATS_DEFAULT,
    rdf_graph_identifier_to_file_stem: Maybe[Callable[[URIRef], str]] = Nothing,
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def skos_file(
        output_config: OutputConfig, skos_graph: skos.Graph.Descriptor
    ) -> None:
        logger = get_dagster_logger()
        output_directory_path = output_config.parse().directory_path / "skos"
        for rdf_file_format in rdf_file_formats:
            logger.info(
                "loading SKOS graph to %s files in %s",
                rdf_file_format.format_.file_extension,
                output_directory_path,
            )
            with (
                RdfDirectoryLoader.create(
                    directory_path=output_directory_path,
                    rdf_file_format=rdf_file_format,
                    rdf_graph_identifier_to_file_stem=rdf_graph_identifier_to_file_stem,
                ) as loader,
                skos.Graph.open(skos_graph, read_only=True) as open_skos_graph,
            ):
                rdflib_graph = open_skos_graph.rdflib_graph
                rdflib_graph.bind("skosxl", SKOSXL)
                loader.load(rdflib_graph)
            logger.info(
                "loaded SKOS graph to %s files in %s",
                rdf_file_format.format_.file_extension,
                output_directory_path,
            )

    return skos_file
