from dagster import AssetsDefinition, PartitionsDefinition, asset
from pathvalidate import sanitize_filename

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import interchange
from graphs2go.resources.output_config import OutputConfig


def build_interchange_file_asset(
    *, partitions_def: PartitionsDefinition | None = None
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def)
    def interchange_file(
        output_config: OutputConfig, interchange_graph: interchange.Graph.Descriptor
    ) -> None:
        output_config_parsed = output_config.parse()

        with RdfDirectoryLoader.create(
            directory_path=output_config_parsed.directory_path
            / "interchange"
            / sanitize_filename(interchange_graph.identifier),
            rdf_format=output_config_parsed.rdf_format,
        ) as loader, interchange.Graph.open(
            interchange_graph
        ) as open_interchange_graph:
            loader.load(open_interchange_graph.to_rdflib_graph())

    return interchange_file
