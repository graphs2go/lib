from collections.abc import Iterable

from dagster import AssetsDefinition, asset, get_dagster_logger
from pathvalidate import sanitize_filename
from graphs2go.models.interchange.dataset import Dataset
from graphs2go.models.interchange.model import Model
from graphs2go.resources.interchange_config import InterchangeConfig


def build_interchange_dataset_asset(
    *, interchange_dataset_name: str, interchange_models: Iterable[Model]
) -> AssetsDefinition:
    @asset(code_version="1")
    def interchange_dataset(interchange_config: InterchangeConfig) -> Dataset:
        interchange_config_parsed = interchange_config.parse()
        logger = get_dagster_logger()

        store_path = interchange_config_parsed.directory_path / sanitize_filename(
            interchange_dataset_name
        )
        if store_path.is_file():
            if interchange_config_parsed.recreate:
                logger.info(
                    "interchange %s already exists but recreate specified, deleting",
                    store_path,
                )
                store_path.unlink()
            else:
                logger.info(
                    "interchange store %s already exists, skipping build", store_path
                )
                return Dataset(store_path=store_path)

        return Dataset(store_path=store_path)

    return interchange_dataset
