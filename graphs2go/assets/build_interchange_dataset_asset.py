from collections.abc import Iterable

from dagster import AssetsDefinition, asset, get_dagster_logger
from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models.interchange.dataset import Dataset
from graphs2go.models.interchange.model import Model
from graphs2go.models.loadable_rdf_graph import LoadableRdfGraph
from graphs2go.resources.interchange_config import InterchangeConfig


def build_interchange_dataset_asset(
    *, interchange_dataset_name: str, interchange_models: Iterable[Model]
) -> AssetsDefinition:
    @asset(code_version="1")
    def interchange_dataset(interchange_config: InterchangeConfig) -> Dataset:
        interchange_config_parsed = interchange_config.parse()
        loader = RdfDirectoryLoader.create(
            directory_path=interchange_config_parsed.directory_path,
            rdf_format=interchange_config_parsed.rdf_format,
        )
        dataset_file_path = loader.stream_file_path(stream=interchange_dataset_name)
        logger = get_dagster_logger()

        if dataset_file_path.is_file():
            if interchange_config_parsed.recreate:
                logger.info(
                    "interchange dataset %s already exists but recreate specified, deleting",
                    dataset_file_path,
                )
                dataset_file_path.unlink()
            else:
                logger.info(
                    "interchange dataset %s already exists, skipping build",
                    dataset_file_path,
                )
                return Dataset(file_path=dataset_file_path)

        for interchange_model in interchange_models:
            loader(
                LoadableRdfGraph(
                    graph=interchange_model.resource.graph,
                    stream=interchange_dataset_name,
                )
            )

        return Dataset(file_path=dataset_file_path)

    return interchange_dataset
