from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar


class RdfStoreConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        directory_path: Path

    directory_path: str

    @classmethod
    def default(cls, *, directory_path_default: Path) -> RdfStoreConfig:
        return RdfStoreConfig(directory_path=str(directory_path_default))

    @classmethod
    def from_env_vars(cls, *, directory_path_default: Path) -> RdfStoreConfig:
        return cls(
            directory_path=EnvVar("OXIGRAPH_DIRECTORY_PATH").get_value(str(directory_path_default)),  # type: ignore
        )

    def parse(self) -> Parsed:
        return RdfStoreConfig.Parsed(
            directory_path=Path(self.directory_path),
        )
