from dagster import AssetsDefinition, asset, get_dagster_logger

import psycopg
from graphs2go.models.postgres_database import PostgresDatabase
from graphs2go.resources.postgres_config import PostgresConfig


def build_postgres_database_asset(*, dbname: str) -> AssetsDefinition:
    @asset(code_version="1")
    def postgres_database(postgres_config: PostgresConfig) -> PostgresDatabase:
        logger = get_dagster_logger()
        with psycopg.connect(postgres_config.conninfo) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                try:
                    cur.execute(f"CREATE DATABASE {dbname};")  # type: ignore
                    logger.info("created database %s", dbname)
                except psycopg.errors.DuplicateDatabase:
                    logger.info("database %s already exists", dbname)

                return PostgresDatabase(conninfo=postgres_config.conninfo, name=dbname)

    return postgres_database
