from dagster import AssetsDefinition, PartitionsDefinition, asset

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models import interchange, rdf
from graphs2go.namespaces.bind_namespaces import bind_namespaces
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.namespaces.skosxl import SKOSXL
from graphs2go.resources.output_config import OutputConfig


def build_interchange_file_asset(
    *,
    partitions_def: PartitionsDefinition | None = None,
    rdf_formats: tuple[rdf.Format, ...] = (rdf.Format.NQUADS,)
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def)
    def interchange_file(
        output_config: OutputConfig, interchange_graph: interchange.Graph.Descriptor
    ) -> None:
        for rdf_format in rdf_formats:
            with RdfDirectoryLoader.create(
                directory_path=output_config.parse().directory_path / "interchange",
                rdf_format=rdf_format,
            ) as loader, interchange.Graph.open(
                interchange_graph, read_only=True
            ) as open_interchange_graph:
                rdflib_graph = open_interchange_graph.rdflib_graph
                bind_namespaces(rdflib_graph)
                loader.load(rdflib_graph)

    return interchange_file
