from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import psycopg
from psycopg import Connection

if TYPE_CHECKING:
    from logging import Logger


@dataclass(frozen=True)
class PostgresDatabase:
    conninfo: str
    name: str

    def connect(self, options: str | None = None) -> Connection:
        return psycopg.connect(self.conninfo, dbname=self.name, options=options)

    @classmethod
    def create(cls, *, conninfo: str, logger: Logger, name: str) -> PostgresDatabase:
        with psycopg.connect(conninfo) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                try:
                    cur.execute(f"CREATE DATABASE {name};")  # type: ignore
                    logger.info("created database %s", name)
                except psycopg.errors.DuplicateDatabase:
                    logger.info("database %s already exists", name)

                return cls(conninfo=conninfo, name=name)
