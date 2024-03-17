import markus
from dagster import get_dagster_logger
from markus.backends.logging import LoggingRollupMetrics


class DagsterLoggingRollupMetrics(LoggingRollupMetrics):
    def __init__(self, *args, **kwds):  # noqa: ANN002, ANN003
        LoggingRollupMetrics.__init__(self, *args, **kwds)
        self.logger = get_dagster_logger()


def configure_markus() -> None:
    markus.configure(
        [
            {
                "class": DagsterLoggingRollupMetrics.__module__
                + "."
                + DagsterLoggingRollupMetrics.__name__,
                "options": {"flush_interval": 30},
            }
        ]
    )
