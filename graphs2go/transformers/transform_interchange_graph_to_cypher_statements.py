from collections.abc import Iterable
from dataclasses import dataclass

import stringcase
from rdflib import URIRef
from rdflib.namespace import NamespaceManager

from graphs2go.models import cypher, interchange
from graphs2go.models.cypher.node_pattern import NodePattern
from graphs2go.transformers.transform_interchange_graph import (
    transform_interchange_graph,
)

_PRIMARY_NODE_LABEL = "Node"


@dataclass(frozen=True)
class _OutputModel:
    cypher_statements: tuple[cypher.Statement, ...]
    interchange_node_uri: URIRef
    interchange_relationship_objects: frozenset[URIRef]


class _UriTransformer:
    def __init__(self, namespace_manager: NamespaceManager):
        self.__namespace_manager = namespace_manager

    def uri_to_curie(self, uri: URIRef) -> tuple[str, str]:
        curie_parts = self.__namespace_manager.curie(uri).split(":", 1)
        assert len(curie_parts) == 2
        return curie_parts[0], curie_parts[1]

    def uri_to_node_id(self, uri: URIRef) -> str:
        return str(uri)

    def uri_to_node_label(self, uri: URIRef) -> str:
        curie = self.uri_to_curie(uri)
        return curie[0].capitalize() + stringcase.pascalcase(curie[1])

    def uri_to_property_name(self, uri: URIRef) -> str:
        curie = self.uri_to_curie(uri)
        return curie[0].lower() + "_" + stringcase.snakecase(curie[1]).lower()

    def uri_to_relationship_label(self, uri: URIRef) -> str:
        curie = self.uri_to_curie(uri)
        return curie[0].upper() + "_" + stringcase.snakecase(curie[1]).upper()


def _transform_interchange_node(
    interchange_node: interchange.Node,
) -> Iterable[_OutputModel]:
    cypher_statements: list[cypher.Statement] = []
    uri_transformer = _UriTransformer(
        namespace_manager=interchange_node.resource.graph.namespace_manager
    )

    interchange_node_secondary_rdf_types = tuple(interchange_node.secondary_rdf_types)

    node_labels: list[str] = [_PRIMARY_NODE_LABEL]

    create_node_statement_builder = cypher.CreateNodeStatement.builder(
        id_=uri_transformer.uri_to_node_id(interchange_node.uri), label=node_labels[0]
    )

    for interchange_node_secondary_rdf_type in interchange_node_secondary_rdf_types:
        create_node_statement_builder.add_label(
            uri_transformer.uri_to_node_label(interchange_node_secondary_rdf_type)
        )

    property_names: set[str] = set()
    for interchange_property in interchange_node.properties:
        property_name = uri_transformer.uri_to_property_name(
            interchange_property.predicate
        )
        property_value = interchange_property.object.toPython()
        create_node_statement_builder.add_property(property_name, property_value)
        property_names.add(property_name)

    for interchange_node_property_name in ("created", "modified"):
        if interchange_node_property_name in property_names:
            continue
        property_value = getattr(interchange_node, interchange_node_property_name)
        if property_value is None:
            continue
        create_node_statement_builder.add_property(
            interchange_node_property_name, property_value
        )

    cypher_statements.append(create_node_statement_builder.build())

    subject_node_pattern = (
        NodePattern.builder()
        .add_label(_PRIMARY_NODE_LABEL)
        .add_property("id", uri_transformer.uri_to_node_id(interchange_node.uri))
        .set_variable("subject")
        .build()
    )
    interchange_relationship_objects: set[URIRef] = set()
    for interchange_relationship in interchange_node.relationships:
        interchange_relationship_object = interchange_relationship.object
        interchange_relationship_objects.add(interchange_relationship_object)

        object_node_pattern: NodePattern = (
            NodePattern.builder()
            .add_label(_PRIMARY_NODE_LABEL)
            .add_property(
                "id", uri_transformer.uri_to_node_id(interchange_relationship_object)
            )
            .set_variable("object")
            .build()
        )

        create_relationship_statement_builder = (
            cypher.CreateRelationshipStatement.builder(
                label=uri_transformer.uri_to_relationship_label(
                    interchange_relationship.predicate
                ),
                object_node_pattern=object_node_pattern,
                subject_node_pattern=subject_node_pattern,
            )
        )

        for interchange_relationship_property_name in ("created", "modified"):
            property_value = getattr(
                interchange_relationship, interchange_relationship_property_name
            )
            if property_value is None:
                continue
            create_relationship_statement_builder.add_property(
                interchange_node_property_name, property_value
            )

        cypher_statements.append(create_relationship_statement_builder.build())

    yield _OutputModel(
        cypher_statements=tuple(cypher_statements),
        interchange_node_uri=interchange_node.uri,
        interchange_relationship_objects=frozenset(interchange_relationship_objects),
    )


def transform_interchange_graph_to_cypher_statements(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
) -> Iterable[cypher.Statement]:
    interchange_node_uris: set[URIRef] = set()
    interchange_relationship_objects: set[URIRef] = set()

    for output_model in transform_interchange_graph(
        interchange_graph_descriptor=interchange_graph_descriptor,
        transform_interchange_node=_transform_interchange_node,
        # in_process=True,
    ):
        interchange_node_uris.add(output_model.interchange_node_uri)
        for (
            interchange_relationship_object
        ) in output_model.interchange_relationship_objects:
            interchange_relationship_objects.add(interchange_relationship_object)

        yield from output_model.cypher_statements

    # Interchange relationship objects that don't refer to interchange nodes should also be represented in the graph.
    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        uri_transformer = _UriTransformer(
            namespace_manager=interchange_graph.rdflib_graph.namespace_manager
        )

        for external_interchange_relation_object in (
            interchange_relationship_objects - interchange_node_uris
        ):
            yield cypher.CreateNodeStatement.builder(
                id_=uri_transformer.uri_to_node_id(
                    external_interchange_relation_object
                ),
                label=_PRIMARY_NODE_LABEL,
            ).build()
