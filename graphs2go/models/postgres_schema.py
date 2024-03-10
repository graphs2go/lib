from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from logging import Logger

    from graphs2go.models.postgres_database import PostgresDatabase


@dataclass(frozen=True)
class PostgresSchema:
    database: PostgresDatabase
    name: str

    @property
    def conninfo(self) -> str:
        return self.database.conninfo + f"?options=-csearch_path%3D{self.name}"

    @classmethod
    def create(
        cls, *, database: PostgresDatabase, logger: Logger, name: str
    ) -> PostgresSchema:
        with database.connect() as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                logger.debug("creating %s schema %s", database.name, name)
                cur.execute(f"CREATE SCHEMA IF NOT EXISTS {name};")  # type: ignore
                logger.info("created %s schema %s", database.name, name)
                return cls(database=database, name=name)
