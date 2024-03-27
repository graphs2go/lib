from datetime import date, datetime
from decimal import Decimal

from graphs2go.models.cypher.property_value import PropertyValue


class Properties(dict[str, PropertyValue]):
    """
    A dict for storing a set of Cypher properties.

    Adapted from Cymple (https://github.com/Accenture/Cymple), MIT license.
    """

    def add(self, key: str, value: PropertyValue) -> None:
        """
        Add a property value. If there is already a value under key, create a sequence with the existing and new value.
        """

        existing_value = self.get(key)
        if existing_value is None:
            self[key] = value
            return

        if isinstance(existing_value, tuple):
            self[key] = (*existing_value, value)
        else:
            self[key] = (existing_value, value)

    @staticmethod
    def __escape_value(string: str) -> str:
        return (
            string.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
        )

    @staticmethod
    def __format_value(key: str, value: PropertyValue) -> str:
        # Assigning a dict to a property is not supported by a neo4j graph
        # if isinstance(value, dict):
        #     return str({sub_key: self._format_value(sub_value) for sub_key, sub_value in value.items()})

        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(
            value, datetime
        ):  # datetime inherits from date, so check it first
            return f'datetime("{value.isoformat()}")'
        if isinstance(value, date):
            return f'date("{value.isoformat()}")'
        if isinstance(value, Decimal | float | int):
            return str(value)
        if isinstance(value, str):
            return '"' + Properties.__escape_value(value) + '"'
        if isinstance(value, tuple):
            return (
                "["
                + ", ".join(
                    Properties.__format_value(key, sub_value) for sub_value in value
                )
                + "]"
            )
        raise TypeError(f"{key}: invalid property value type {type(value)}")

    def __str__(self) -> str:
        return ", ".join(
            f"{key}: {Properties.__format_value(key, value)}"
            for key, value in self.items()
        )
