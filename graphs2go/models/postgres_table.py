from dataclasses import dataclass

from graphs2go.models.postgres_schema import PostgresSchema


@dataclass(frozen=True)
class PostgresTable:
    name: str
    schema: PostgresSchema
