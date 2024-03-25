from typing import Any


class Properties(dict):
    """
    A dict for storing a set of Cypher properties.

    Adapted from Cymple (https://github.com/Accenture/Cymple), MIT license.
    """

    @staticmethod
    def __escape(string: str) -> str:
        res = (
            string.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
        )
        return res

    @staticmethod
    def __format_value(value: Any, *, escape: bool) -> Any:
        # Assigning a dict to a property is not supported by a neo4j graph
        # if isinstance(value, dict):
        #     return str({sub_key: self._format_value(sub_value) for sub_key, sub_value in value.items()})
        if escape and isinstance(value, str):
            return f'"{Properties.__escape(value)}"'
        if value is None:
            return "null"

        return value

    def __str__(self) -> str:
        return ", ".join(
            f"{key}: {Properties.__format_value(value, escape=True)}"
            for key, value in self.items()
        )
