from dataclasses import dataclass

from psycopg import Connection
import psycopg


@dataclass(frozen=True)
class PostgresDatabase:
    conninfo: str
    name: str

    def connect(self, options: str | None = None) -> Connection:
        return psycopg.connect(self.conninfo, dbname=self.name, options=options)
