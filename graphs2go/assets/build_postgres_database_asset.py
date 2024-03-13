from dagster import AssetsDefinition, asset, get_dagster_logger

from graphs2go.models.postgres_database import PostgresDatabase
from graphs2go.resources.postgres_connection_pool import PostgresConnectionPool


def build_postgres_database_asset(*, dbname: str) -> AssetsDefinition:
    @asset(code_version="1")
    def postgres_database(
        postgres_connection_pool: PostgresConnectionPool,
    ) -> PostgresDatabase:
        return PostgresDatabase.create(
            connection_pool=postgres_connection_pool,
            logger=get_dagster_logger(),
            name=dbname,
        )

    return postgres_database
