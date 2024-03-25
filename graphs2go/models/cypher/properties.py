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
            self[key] = tuple(list(existing_value) + [value])
        else:
            self[key] = (existing_value, value)

    @staticmethod
    def __escape_value(string: str) -> str:
        res = (
            string.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
        )
        return res

    @staticmethod
    def __format_value(value: PropertyValue, *, escape: bool) -> PropertyValue:
        # Assigning a dict to a property is not supported by a neo4j graph
        # if isinstance(value, dict):
        #     return str({sub_key: self._format_value(sub_value) for sub_key, sub_value in value.items()})

        if escape and isinstance(value, str):
            return f'"{Properties.__escape_value(value)}"'

        if value is None:
            return "null"

        return value

    def __str__(self) -> str:
        return ", ".join(
            f"{key}: {Properties.__format_value(value, escape=True)}"
            for key, value in self.items()
        )
