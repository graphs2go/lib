from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar

from graphs2go.models import rdf


class OutputConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        directory_path: Path
        rdf_format: rdf.Format

    directory_path: str
    rdf_format: str

    @classmethod
    def default(cls, *, directory_path_default: Path) -> OutputConfig:
        return OutputConfig(directory_path=str(directory_path_default), rdf_format="")

    @classmethod
    def from_env_vars(cls, *, directory_path_default: Path) -> OutputConfig:
        return cls(
            directory_path=EnvVar("GRAPHS2GO_OUTPUT_DIRECTORY_PATH").get_value(str(directory_path_default)),  # type: ignore
            rdf_format=EnvVar("GRAPHS2GO_RDF_FORMAT").get_value(""),  # type: ignore
        )

    def parse(self) -> Parsed:
        return OutputConfig.Parsed(
            directory_path=Path(self.directory_path),
            rdf_format=(
                getattr(rdf.Format, self.rdf_format.upper())
                if self.rdf_format
                else rdf.Format.NQUADS
            ),
        )
