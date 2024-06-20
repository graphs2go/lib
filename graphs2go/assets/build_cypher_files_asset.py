from dagster import AssetsDefinition, PartitionsDefinition, asset, get_dagster_logger
from returns.maybe import Maybe, Nothing
from tqdm import tqdm

from graphs2go.loaders.cypher_directory_loader import CypherDirectoryLoader
from graphs2go.models import interchange
from graphs2go.resources.output_config import OutputConfig
from graphs2go.transformers.transform_interchange_graph_to_cypher_statements import (
    transform_interchange_graph_to_cypher_statements,
)


def build_cypher_files_asset(
    *, partitions_def: Maybe[PartitionsDefinition] = Nothing
) -> AssetsDefinition:
    @asset(code_version="1", partitions_def=partitions_def.value_or(None))
    def cypher_files(
        interchange_graph: interchange.Graph.Descriptor, output_config: OutputConfig
    ) -> None:
        logger = get_dagster_logger()
        cypher_directory_path = output_config.parse().directory_path / "cypher"

        with CypherDirectoryLoader(directory_path=cypher_directory_path) as loader:
            logger.info("loading Cypher files to %s", cypher_directory_path)
            for cypher_statement in tqdm(
                transform_interchange_graph_to_cypher_statements(interchange_graph),
                desc="Cypher statements",
            ):
                loader.load(cypher_statement)
            logger.info("loaded Cypher files to %s", cypher_directory_path)

    return cypher_files
