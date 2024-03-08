from __future__ import annotations

from dagster import ConfigurableResource, EnvVar


class PostgresConfig(ConfigurableResource):  # type: ignore
    conninfo: str
    truncate: bool

    @classmethod
    def from_env_vars(cls) -> PostgresConfig:
        return cls(
            conninfo=EnvVar("POSTGRES_CONNINFO"),
            truncate=EnvVar.int("POSTGRES_TRUNCATE") == 1,
        )
