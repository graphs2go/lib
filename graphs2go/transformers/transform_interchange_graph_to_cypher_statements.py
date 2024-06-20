from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import stringcase
from rdflib import URIRef
from rdflib.namespace import NamespaceManager
from returns.pipeline import is_successful

from graphs2go.models import cypher, interchange
from graphs2go.models.cypher.node_pattern import NodePattern
from graphs2go.transformers.transform_interchange_graph import (
    transform_interchange_graph,
)

if TYPE_CHECKING:
    from datetime import datetime

    from returns.maybe import Maybe

_PRIMARY_NODE_LABEL = "Node"


@dataclass(frozen=True)
class _OutputModel:
    cypher_statements: tuple[cypher.Statement, ...]
    interchange_node_iri: URIRef
    interchange_relationship_objects: frozenset[URIRef]


class _UriTransformer:
    def __init__(self, namespace_manager: NamespaceManager):
        self.__namespace_manager = namespace_manager

    def iri_to_curie(self, iri: URIRef) -> tuple[str, str]:
        curie_parts = self.__namespace_manager.curie(iri).split(":", 1)
        assert len(curie_parts) == 2
        return curie_parts[0], curie_parts[1]

    def iri_to_node_id(self, iri: URIRef) -> str:
        return str(iri)

    def iri_to_node_label(self, iri: URIRef) -> str:
        curie = self.iri_to_curie(iri)
        return curie[0].capitalize() + stringcase.pascalcase(curie[1])

    def iri_to_property_name(self, iri: URIRef) -> str:
        curie = self.iri_to_curie(iri)
        return curie[0].lower() + "_" + stringcase.snakecase(curie[1]).lower()

    def iri_to_relationship_label(self, iri: URIRef) -> str:
        curie = self.iri_to_curie(iri)
        return curie[0].upper() + "_" + stringcase.snakecase(curie[1]).upper()


def _transform_interchange_node(
    interchange_node: interchange.Node,
) -> Iterable[_OutputModel]:
    cypher_statements: list[cypher.Statement] = []
    iri_transformer = _UriTransformer(
        namespace_manager=interchange_node.resource.graph.namespace_manager
    )

    node_labels: list[str] = [_PRIMARY_NODE_LABEL]

    create_node_statement_builder = cypher.CreateNodeStatement.builder(
        id_=iri_transformer.iri_to_node_id(interchange_node.iri), label=node_labels[0]
    )

    for type_iri in interchange_node.types:
        create_node_statement_builder.add_label(
            iri_transformer.iri_to_node_label(type_iri)
        )

    property_names: set[str] = set()
    for interchange_property in interchange_node.properties():
        property_name = iri_transformer.iri_to_property_name(
            interchange_property.predicate
        )
        interchange_property_value = interchange_property.object.toPython()
        create_node_statement_builder.add_property(
            property_name, interchange_property_value
        )
        property_names.add(property_name)

    for interchange_node_property_name in ("created", "modified"):
        if interchange_node_property_name in property_names:
            continue
        interchange_node_property_value: Maybe[datetime] = getattr(
            interchange_node, interchange_node_property_name
        )
        if not is_successful(interchange_node_property_value):
            continue
        create_node_statement_builder.add_property(
            interchange_node_property_name,
            interchange_node_property_value.unwrap(),
        )

    cypher_statements.append(create_node_statement_builder.build())

    subject_node_pattern = (
        NodePattern.builder()
        .add_label(_PRIMARY_NODE_LABEL)
        .add_property("id", iri_transformer.iri_to_node_id(interchange_node.iri))
        .set_variable("subject")
        .build()
    )
    interchange_relationship_objects: set[URIRef] = set()
    for interchange_relationship in interchange_node.relationships():
        interchange_relationship_object = interchange_relationship.object
        interchange_relationship_objects.add(interchange_relationship_object)

        object_node_pattern: NodePattern = (
            NodePattern.builder()
            .add_label(_PRIMARY_NODE_LABEL)
            .add_property(
                "id", iri_transformer.iri_to_node_id(interchange_relationship_object)
            )
            .set_variable("object")
            .build()
        )

        create_relationship_statement_builder = (
            cypher.CreateRelationshipStatement.builder(
                label=iri_transformer.iri_to_relationship_label(
                    interchange_relationship.predicate
                ),
                object_node_pattern=object_node_pattern,
                subject_node_pattern=subject_node_pattern,
            )
        )

        for interchange_relationship_property_name in ("created", "modified"):
            interchange_relationship_property_value: Maybe[datetime] = getattr(
                interchange_relationship, interchange_relationship_property_name
            )
            if not is_successful(interchange_relationship_property_value):
                continue
            create_relationship_statement_builder.add_property(
                interchange_node_property_name,
                interchange_relationship_property_value.unwrap(),
            )

        cypher_statements.append(create_relationship_statement_builder.build())

    yield _OutputModel(
        cypher_statements=tuple(cypher_statements),
        interchange_node_iri=interchange_node.iri,
        interchange_relationship_objects=frozenset(interchange_relationship_objects),
    )


def transform_interchange_graph_to_cypher_statements(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
) -> Iterable[cypher.Statement]:
    interchange_node_iris: set[URIRef] = set()
    interchange_relationship_objects: set[URIRef] = set()

    output_model: _OutputModel
    for output_model in transform_interchange_graph(
        interchange_graph_descriptor=interchange_graph_descriptor,
        transform_interchange_node=_transform_interchange_node,
        # in_process=True,
    ):
        interchange_node_iris.add(output_model.interchange_node_iri)  # type: ignore
        for (
            interchange_relationship_object
        ) in output_model.interchange_relationship_objects:  # type: ignore
            interchange_relationship_objects.add(interchange_relationship_object)

        yield from output_model.cypher_statements  # type: ignore

    # Interchange relationship objects that don't refer to interchange nodes should also be represented in the graph.
    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        iri_transformer = _UriTransformer(
            namespace_manager=interchange_graph.rdflib_graph.namespace_manager
        )

        for external_interchange_relation_object in (
            interchange_relationship_objects - interchange_node_iris
        ):
            yield cypher.CreateNodeStatement.builder(
                id_=iri_transformer.iri_to_node_id(
                    external_interchange_relation_object
                ),
                label=_PRIMARY_NODE_LABEL,
            ).build()
