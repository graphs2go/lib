from dagster import AssetsDefinition, asset, get_dagster_logger

from graphs2go.models.postgres_database import PostgresDatabase
from graphs2go.resources.postgres_config import PostgresConfig


def build_postgres_database_asset(*, dbname: str) -> AssetsDefinition:
    @asset(code_version="1")
    def postgres_database(postgres_config: PostgresConfig) -> PostgresDatabase:
        return PostgresDatabase.create(
            conninfo=postgres_config.conninfo, logger=get_dagster_logger(), name=dbname
        )

    return postgres_database
