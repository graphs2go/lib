from __future__ import annotations
from contextlib import contextmanager
from dagster import ConfigurableResource, EnvVar
from psycopg_pool import ConnectionPool
from graphs2go.models.postgres_database import PostgresDatabase
from graphs2go.models.postgres_schema import PostgresSchema
from graphs2go.models.postgres_tables import PostgresTables
from typing import TYPE_CHECKING, Any
from time import monotonic

if TYPE_CHECKING:
    from collections.abc import Iterator
    from psycopg import Connection


class PostgresConnectionPool(ConfigurableResource):
    conninfo: str

    def __init__(self, *args, **kwds):  # noqa: ANN002, ANN003
        ConfigurableResource.__init__(self, *args, **kwds)
        self.__connection_pools: dict[str, dict[str | None, ConnectionPool]] = {}

    @classmethod
    def from_env_vars(cls) -> PostgresConnectionPool:
        return cls(conninfo=EnvVar("POSTGRES_CONNINFO").get_value())

    @contextmanager
    def connect(
        self, to: PostgresDatabase | PostgresSchema | PostgresTables
    ) -> Iterator[Connection[Any]]:
        if isinstance(to, PostgresDatabase):
            database_name = to.name
            schema_name = None
        elif isinstance(to, PostgresSchema):
            database_name = to.database.name
            schema_name = to.name
        elif isinstance(to, PostgresTables):
            database_name = to.schema.database.name
            schema_name = to.schema.name
        else:
            raise TypeError(to)

        connection_pool = self.__connection_pools.setdefault(database_name, {}).get(
            schema_name
        )
        if connection_pool is None:
            connection_pool_kwds = {"dbname": database_name}
            if schema_name is not None:
                connection_pool_kwds["options"] = f"-c search_path={schema_name}"
            connection_pool = ConnectionPool(
                conninfo=self.conninfo,
                kwargs=connection_pool_kwds,
                max_size=8,  # Otherwise it defaults to min_size
                min_size=1,
                timeout=5,  # Fail quickly if the pool is exhausted
            )
            self.__connection_pools[database_name][schema_name] = connection_pool

        # Adapted from ConnectionPool.connection()
        conn = connection_pool.getconn()
        try:
            t0 = monotonic()
            with conn:
                yield conn
        finally:
            connection_pool.putconn(conn)
            t1 = monotonic()
            connection_pool._stats[connection_pool._USAGE_MS] += int(  # noqa: SLF001
                1000.0 * (t1 - t0)
            )
