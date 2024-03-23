from __future__ import annotations

from dagster import ConfigurableResource, EnvVar


class PostgresConfig(ConfigurableResource):  # type: ignore
    conninfo: str

    @classmethod
    def from_env_vars(cls) -> PostgresConfig:
        return cls(conninfo=EnvVar("POSTGRES_CONNINFO"))
