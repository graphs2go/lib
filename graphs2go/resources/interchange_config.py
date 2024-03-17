from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar
from graphs2go.models.rdf_format import RdfFormat
from graphs2go.utils.parse_directory_path_config_value import (
    parse_directory_path_config_value,
)


class InterchangeConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        directory_path: Path
        rdf_format: RdfFormat
        recreate: bool

    directory_path: str
    rdf_format: str
    recreate: bool

    @classmethod
    def default(cls) -> InterchangeConfig:
        return InterchangeConfig(directory_path="", rdf_format="", recreate=False)

    @classmethod
    def from_env_vars(cls) -> InterchangeConfig:
        return cls(
            directory_path=EnvVar("INTERCHANGE_DIRECTORY_PATH").get_value(""),  # type: ignore
            rdf_format=EnvVar("INTERCHANGE_RDF_FORMAT").get_value(""),  # type: ignore
            recreate=EnvVar.int("INTERCHANGE_RECREATE").get_value() == 1,
        )

    def parse(self) -> Parsed:
        return InterchangeConfig.Parsed(
            directory_path=parse_directory_path_config_value(
                self.directory_path,
                default=Path(__file__).parent.parent.parent / "data" / "interchange",
            ),
            rdf_format=(
                getattr(RdfFormat, self.rdf_format.upper())
                if self.rdf_format
                else RdfFormat.NQUADS
            ),
            recreate=self.recreate,
        )
