from __future__ import annotations

from contextlib import contextmanager
from time import monotonic
from typing import TYPE_CHECKING, Any

import markus
from dagster import ConfigurableResource, EnvVar
from psycopg_pool import ConnectionPool

from graphs2go.models import postgres

if TYPE_CHECKING:
    from collections.abc import Iterator

    from psycopg import Connection


metrics = markus.get_metrics(__name__)


class PostgresConnectionPool(ConfigurableResource):  # type: ignore
    conninfo: str

    def __init__(self, *args, **kwds) -> None:  # noqa: ANN002, ANN003
        ConfigurableResource.__init__(self, *args, **kwds)
        self.__connection_pools: dict[str | None, dict[str | None, ConnectionPool]] = {}

    def close(self) -> None:
        for database_connection_pools in self.__connection_pools.values():
            for schema_connection_pool in database_connection_pools.values():
                schema_connection_pool.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: ANN001
        self.close()

    @classmethod
    def from_env_vars(cls) -> PostgresConnectionPool:
        return cls(conninfo=EnvVar("POSTGRES_CONNINFO").get_value())

    @contextmanager
    def connect(
        self, to: postgres.Database | postgres.Schema | postgres.Tables | None
    ) -> Iterator[Connection[Any]]:
        database_name = None
        schema_name = None
        if to is None:
            pass
        elif isinstance(to, postgres.Database):
            database_name = to.name
        elif isinstance(to, postgres.Schema):
            database_name = to.database.name
            schema_name = to.name
        elif isinstance(to, postgres.Tables):
            database_name = to.schema.database.name
            schema_name = to.schema.name
        else:
            raise TypeError(to)

        connection_pool = self.__connection_pools.setdefault(database_name, {}).get(
            schema_name
        )
        if connection_pool is None:
            connection_pool_kwds = {}
            if database_name is not None:
                connection_pool_kwds["dbname"] = database_name
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
        with metrics.timer("connection_pool_getconn"):
            conn = connection_pool.getconn()
        try:
            t0 = monotonic()
            with conn:
                yield conn
        finally:
            connection_pool.putconn(conn)
            t1 = monotonic()
            connection_pool._stats[connection_pool._USAGE_MS] += int(1000.0 * (t1 - t0))
