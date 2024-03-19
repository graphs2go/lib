import dataclasses
from dataclasses import dataclass

from graphs2go.models.postgres.schema import Schema
from graphs2go.models.postgres.table import Table


@dataclass(frozen=True)
class Tables:
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
    def schema(self) -> Schema:
        return self._tables[0].schema

    @property
    def _tables(self) -> tuple[Table, ...]:
        result: list[Table] = []
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            assert isinstance(value, Table)
            result.append(value)
        return tuple(result)
