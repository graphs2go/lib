from __future__ import annotations
from dataclasses import dataclass
from typing import Self

from graphs2go.models.cypher import Properties
from graphs2go.models.cypher.property_value import PropertyValue


@dataclass(frozen=True)
class NodePattern:
    value: str

    class Builder:
        def __init__(self):
            self.__labels = []
            self.__properties = Properties()
            self.__variable = ""

        def add_label(self, label: str) -> Self:
            self.__labels.append(label)
            return self

        def add_property(self, name: str, value: PropertyValue) -> Self:
            self.__properties.add(name, value)
            return self

        def build(self) -> NodePattern:
            if not self.__labels:
                raise ValueError("must add at least one label")
            parts = [f"{self.__variable}:{':'.join(self.__labels)}"]
            if self.__properties:
                parts.append("{" + str(self.__properties) + "}")
            return NodePattern("(" + " ".join(parts) + ")")

    @classmethod
    def builder(cls) -> Builder:
        return cls.builder()
