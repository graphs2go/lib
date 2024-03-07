from abc import ABC, abstractmethod
from dataclasses import dataclass
from graphs2go.models.postgres_schema import PostgresSchema

from graphs2go.models.postgres_table import PostgresTable


@dataclass(frozen=True)
class PostgresTables(ABC):
    def _post_init(self) -> None:
        database_names: set[str] = set()
        schema_names: set[str] = set()
        for table in self._tables:
            database_names.add(table.schema.database.name)
            schema_names.add(table.schema.name)
        if len(database_names) > 1:
            raise ValueError(
                "tables in different databases: " + " ".join(database_names)
            )
        if len(schema_names) > 1:
            raise ValueError("tables in different schemas: " + " ".join(schema_names))

    @property
    def schema(self) -> PostgresSchema:
        return self._tables[0].schema

    @property
    @abstractmethod
    def _tables(self) -> tuple[PostgresTable, ...]:
        raise NotImplementedError
