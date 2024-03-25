from __future__ import annotations

from typing import TYPE_CHECKING, Self

from graphs2go.models.cypher.node_pattern import NodePattern
from graphs2go.models.cypher.statement import Statement

if TYPE_CHECKING:
    from graphs2go.models.cypher.property_value import PropertyValue


class CreateNodeStatement(Statement):
    class Builder(Statement.Builder):
        def __init__(self):
            self.__node_pattern_builder = NodePattern.builder()

        def add_label(self, label: str) -> Self:
            self.__node_pattern_builder.add_label(label)
            return self

        def add_property(self, name: str, value: PropertyValue) -> Self:
            self.__node_pattern_builder.add_property(name, value)
            return self

        def build(self) -> CreateNodeStatement:
            return CreateNodeStatement(
                cypher_str=f"CREATE {self.__node_pattern_builder.build().cypher_str};"
            )

    @classmethod
    def builder(cls, *, id_: str, label: str) -> Builder:
        builder = cls.Builder()
        builder.add_label(label)
        builder.add_property("id", id_)
        return builder
