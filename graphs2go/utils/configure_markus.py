import markus


def configure_markus() -> None:
    markus.configure(
        [
            {
                "class": "markus.backends.logging.LoggingMetrics",
            }
        ]
    )
