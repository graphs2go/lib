from dagster import AssetsDefinition, PartitionsDefinition, asset
from pathvalidate import sanitize_filename

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import skos
from graphs2go.resources.output_config import OutputConfig


def build_skos_file_asset(
    *, partitions_def: PartitionsDefinition | None = None
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def)
    def skos_file(
        output_config: OutputConfig, skos_graph: skos.Graph.Descriptor
    ) -> None:
        output_config_parsed = output_config.parse()

        with RdfDirectoryLoader.create(
            directory_path=output_config_parsed.directory_path
            / "skos"
            / sanitize_filename(skos_graph.identifier),
            rdf_format=output_config_parsed.rdf_format,
        ) as loader, skos.Graph.open(skos_graph) as open_skos_graph:
            loader.load(open_skos_graph.to_rdflib_graph())

    return skos_file
