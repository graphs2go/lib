from dagster import AssetsDefinition, PartitionsDefinition, asset

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import rdf, skos
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.resources.output_config import OutputConfig


def build_skos_file_asset(
    *,
    partitions_def: PartitionsDefinition | None = None,
    rdf_formats: tuple[rdf.Format, ...] = (rdf.Format.NQUADS,)
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def)
    def skos_file(
        output_config: OutputConfig, skos_graph: skos.Graph.Descriptor
    ) -> None:
        for rdf_format in rdf_formats:
            with RdfDirectoryLoader.create(
                directory_path=output_config.parse().directory_path / "skos",
                rdf_format=rdf_format,
            ) as loader, skos.Graph.open(skos_graph) as open_skos_graph:
                rdflib_graph = open_skos_graph.rdflib_graph
                rdflib_graph.bind("skosxl", SKOSXL)
                loader.load(rdflib_graph)

    return skos_file
