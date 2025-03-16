from __future__ import annotations

from typing import TYPE_CHECKING, Self

from graphs2go.models.cypher.properties import Properties
from graphs2go.models.cypher.statement import Statement

if TYPE_CHECKING:
    from graphs2go.models.cypher.node_pattern import NodePattern
    from graphs2go.models.cypher.property_value import PropertyValue


class CreateRelationshipStatement(Statement):
    class Builder(Statement.Builder):
        def __init__(
            self,
            *,
            label: str,
            object_node_pattern: NodePattern,
            subject_node_pattern: NodePattern,
        ):
            self.__label = label
            self.__properties = Properties()
            assert object_node_pattern.variable
            self.__object_node_pattern = object_node_pattern
            assert subject_node_pattern.variable
            self.__subject_node_pattern = subject_node_pattern

        def add_property(self, name: str, value: PropertyValue) -> Self:
            self.__properties.add(name, value)
            return self

        def build(self) -> CreateRelationshipStatement:
            return CreateRelationshipStatement(
                cypher_str=f"""\
MATCH {self.__subject_node_pattern.cypher_str}, {self.__object_node_pattern.cypher_str}
CREATE ({self.__subject_node_pattern.variable})-[:{self.__label}{" {" + str(self.__properties) + "}" if self.__properties else ""}]->({self.__object_node_pattern.variable});"""
            )

    @classmethod
    def builder(
        cls,
        *,
        label: str,
        object_node_pattern: NodePattern,
        subject_node_pattern: NodePattern,
    ) -> Builder:
        return cls.Builder(
            label=label,
            object_node_pattern=object_node_pattern,
            subject_node_pattern=subject_node_pattern,
        )
