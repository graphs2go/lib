from __future__ import annotations

from dagster import ConfigurableResource, EnvVar


class PostgresConfig(ConfigurableResource):  # type: ignore
    conninfo: str
    recreate: bool

    @classmethod
    def from_env_vars(cls) -> PostgresConfig:
        return cls(
            conninfo=EnvVar("POSTGRES_CONNINFO"),
            recreate=EnvVar.int("POSTGRES_RECREATE") == 1,
        )
