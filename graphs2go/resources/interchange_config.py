from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar
from graphs2go.utils.parse_directory_path_config_value import (
    parse_directory_path_config_value,
)


class InterchangeConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        interchange_directory_path: Path

    interchange_directory_path: str

    @classmethod
    def default(cls) -> InterchangeConfig:
        return InterchangeConfig(
            interchange_directory_path="",
        )

    @classmethod
    def from_env_vars(cls) -> InterchangeConfig:
        return cls(
            interchange_directory_path=EnvVar("INTERCHANGE_DIRECTORY_PATH").get_value(""),  # type: ignore
        )

    def parse(self) -> Parsed:
        return InterchangeConfig.Parsed(
            interchange_directory_path=parse_directory_path_config_value(
                self.interchange_directory_path,
                default=Path(__file__).parent.parent.parent / "data" / "interchange",
            )
        )
