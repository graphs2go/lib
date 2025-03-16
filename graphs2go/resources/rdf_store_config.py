from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dagster import ConfigurableResource, EnvVar
from returns.maybe import Maybe, Nothing, Some

_TRANSACTIONAL_DEFAULT = False


class RdfStoreConfig(ConfigurableResource):  # type: ignore
    @dataclass(frozen=True)
    class Parsed:
        directory_path: Maybe[Path]
        transactional: bool

    directory_path: str
    transactional: bool

    @classmethod
    def default(cls, *, directory_path_default: Maybe[Path]) -> RdfStoreConfig:
        return RdfStoreConfig(
            directory_path=str(directory_path_default.value_or("")),
            transactional=_TRANSACTIONAL_DEFAULT,
        )

    @classmethod
    def from_env_vars(cls, *, directory_path_default: Maybe[Path]) -> RdfStoreConfig:
        return cls(
            directory_path=EnvVar("OXIGRAPH_DIRECTORY_PATH").get_value(
                str(directory_path_default.value_or(""))
            ),  # type: ignore
            transactional=EnvVar.int("RDF_STORE_TRANSACTIONAL").get_value(
                1 if _TRANSACTIONAL_DEFAULT else 0
            )
            == 1,
        )

    def parse(self) -> Parsed:
        return RdfStoreConfig.Parsed(
            directory_path=(
                Some(Path(self.directory_path)) if self.directory_path else Nothing
            ),
            transactional=self.transactional,
        )
