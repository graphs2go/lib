from collections.abc import Iterable

from dagster import AssetsDefinition, asset
from graphs2go.models.interchange.dataset import Dataset
from graphs2go.models.interchange.model import Model
from graphs2go.resources.interchange_config import InterchangeConfig


def build_interchange_dataset_asset(*, models: Iterable[Model]) -> AssetsDefinition:
    @asset(code_version="1")
    def interchange_dataset(interchange_config: InterchangeConfig) -> Dataset:

        pass

    return _asset
