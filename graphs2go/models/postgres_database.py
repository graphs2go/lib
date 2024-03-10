from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from graphs2go.resources.postgres_connection_pool import PostgresConnectionPool


if TYPE_CHECKING:
    from logging import Logger


@dataclass(frozen=True)
class PostgresDatabase:
    name: str

    @classmethod
    def create(
        cls, *, connection_pool: PostgresConnectionPool, logger: Logger, name: str
    ) -> PostgresDatabase:
        with connection_pool.connect(self) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(f"CREATE DATABASE {name};")  # type: ignore
                    logger.info("created database %s", name)
                except psycopg.errors.DuplicateDatabase:
                    logger.info("database %s already exists", name)

                return cls(conninfo=conninfo, name=name)
