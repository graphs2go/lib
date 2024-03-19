from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar

from graphs2go.utils.parse_directory_path_config_value import (
    parse_directory_path_config_value,
)


class OxigraphConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        directory_path: Path

    directory_path: str

    @classmethod
    def default(cls) -> OxigraphConfig:
        return OxigraphConfig(directory_path="")

    @classmethod
    def from_env_vars(cls) -> OxigraphConfig:
        return cls(
            directory_path=EnvVar("OXIGRAPH_DIRECTORY_PATH").get_value(""),  # type: ignore
        )

    def parse(self) -> Parsed:
        return OxigraphConfig.Parsed(
            directory_path=parse_directory_path_config_value(
                self.directory_path,
                default=Path(__file__).parent.parent.parent / "data" / "oxigraph",
            ),
        )
