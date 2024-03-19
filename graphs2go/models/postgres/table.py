from dataclasses import dataclass

from graphs2go.models.postgres.schema import Schema


@dataclass(frozen=True)
class Table:
    name: str
    schema: Schema
