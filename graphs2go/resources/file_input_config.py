from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar


class FileInputConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        file_path: Path

    file_path: str

    @classmethod
    def default(cls, *, file_path_default: Path) -> FileInputConfig:
        return FileInputConfig(file_path=str(file_path_default))

    @classmethod
    def from_env_vars(cls, *, file_path_default: Path) -> FileInputConfig:
        return cls(
            file_path=EnvVar("GRAPHS2GO_INPUT_FILE_PATH").get_value(
                str(file_path_default)
            ),  # type: ignore
        )

    def parse(self) -> Parsed:
        return FileInputConfig.Parsed(file_path=Path(self.file_path))
