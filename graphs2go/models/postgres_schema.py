from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from graphs2go.models.postgres_database import PostgresDatabase
    from graphs2go.resources.postgres_connection_pool import PostgresConnectionPool


@dataclass(frozen=True)
class PostgresSchema:
    database: PostgresDatabase
    name: str

    @classmethod
    def create(
        cls,
        *,
        connection_pool: PostgresConnectionPool,
        database: PostgresDatabase,
        logger: Logger,
        name: str,
    ) -> PostgresSchema:
        with connection_pool.connect(database) as conn, conn.cursor() as cur:
            logger.debug("creating %s schema %s", database.name, name)
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {name};")  # type: ignore
            logger.info("created %s schema %s", database.name, name)
            return cls(database=database, name=name)
