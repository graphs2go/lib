from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from graphs2go.models.postgres.database import Database
    from graphs2go.resources.postgres_connection_pool import PostgresConnectionPool


@dataclass(frozen=True)
class Schema:
    database: Database
    name: str

    @classmethod
    def create(
        cls,
        *,
        connection_pool: PostgresConnectionPool,
        database: Database,
        logger: Logger,
        name: str,
    ) -> Schema:
        with connection_pool.connect(database) as conn, conn.cursor() as cur:
            logger.debug("creating %s schema %s", database.name, name)
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {name};")  # type: ignore
            logger.info("created %s schema %s", database.name, name)
            return cls(database=database, name=name)
