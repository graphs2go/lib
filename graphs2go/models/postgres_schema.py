from dataclasses import dataclass

from psycopg import Connection
from graphs2go.models.postgres_database import PostgresDatabase


@dataclass(frozen=True)
class PostgresSchema:
    database: PostgresDatabase
    name: str

    def connect(self) -> Connection:
        return self.database.connect(options=f"-c search_path={self.name}")
