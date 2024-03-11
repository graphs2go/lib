from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import psycopg.errors

if TYPE_CHECKING:
    from logging import Logger

    from graphs2go.resources.postgres_connection_pool import PostgresConnectionPool


@dataclass(frozen=True)
class PostgresDatabase:
    name: str

    @classmethod
    def create(
        cls, *, connection_pool: PostgresConnectionPool, logger: Logger, name: str
    ) -> PostgresDatabase:
        inst = cls(name=name)
        with connection_pool.connect(inst) as conn:
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    try:
                        cur.execute(f"CREATE DATABASE {name};")  # type: ignore
                        logger.info("created database %s", name)
                    except psycopg.errors.DuplicateDatabase:
                        logger.info("database %s already exists", name)
            finally:
                conn.autocommit = False

            return inst
