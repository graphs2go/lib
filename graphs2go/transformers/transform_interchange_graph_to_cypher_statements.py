from collections.abc import Iterable

import stringcase
from dagster import get_dagster_logger
from rdflib import URIRef

from graphs2go.models import interchange, cypher
from graphs2go.models.cypher.node_pattern import NodePattern


_PRIMARY_NODE_LABEL = "NODE"


def transform_interchange_graph_to_cypher_statements(
    interchange_graph: interchange.Graph,
) -> Iterable[cypher.Statement]:
    logger = get_dagster_logger()

    def uri_to_curie(uri: URIRef) -> tuple[str, str]:
        curie_parts = interchange_graph.rdflib_graph.namespace_manager.curie(uri).split(
            ":", 1
        )
        assert len(curie_parts) == 2
        return tuple(curie_parts)

    def uri_to_node_id(uri: URIRef) -> str:
        return str(uri)

    def uri_to_node_label(uri: URIRef) -> str:
        curie = uri_to_curie(uri)
        return curie[0].capitalize() + stringcase.pascalcase(curie[1])

    def uri_to_property_name(uri: URIRef) -> str:
        curie = uri_to_curie(uri)
        return curie[0].lower() + "_" + stringcase.snakecase(curie[1]).lower()

    def uri_to_relationship_label(uri: URIRef) -> str:
        curie = uri_to_curie(uri)
        return curie[0].upper() + "_" + stringcase.snakecase(curie[1]).upper()

    interchange_node_uris: set[URIRef] = set()
    interchange_relationship_objects: set[URIRef] = set()

    for interchange_node in interchange_graph.nodes():
        interchange_node_uris.add(interchange_node.uri)

        interchange_node_secondary_rdf_types = tuple(
            interchange_node.secondary_rdf_types
        )

        node_labels: list[str] = [_PRIMARY_NODE_LABEL]

        create_node_statement_builder = cypher.CreateNodeStatement.builder(
            id_=uri_to_node_id(interchange_node.uri), label=node_labels[0]
        )

        for interchange_node_secondary_rdf_type in interchange_node_secondary_rdf_types:
            create_node_statement_builder.add_label(
                uri_to_node_label(interchange_node_secondary_rdf_type)
            )

        property_names: set[str] = set()
        for interchange_property in interchange_node.properties:
            property_value = interchange_property.object.toPython()
            if not isinstance(property_value, cypher.PropertyValue):
                logger.warning(
                    "interchange node %s property %s has an incompatible value type: %s",
                    interchange_node.uri,
                    interchange_property.predicate,
                    type(property_value),
                )
                continue

            property_name = uri_to_property_name(interchange_property.predicate)
            create_node_statement_builder.add_property(property_name, property_value)
            property_names.add(property_name)

        for interchange_node_property_name in ("created", "modified"):
            if interchange_node_property_name in property_names:
                continue
            property_value = getattr(interchange_node, interchange_node_property_name)
            if property_value is None:
                continue
            assert isinstance(property_value, cypher.PropertyValue)
            create_node_statement_builder.add_property(
                interchange_node_property_name, property_value
            )

        yield create_node_statement_builder.build()

        subject_node_pattern = (
            NodePattern.builder()
            .add_label(_PRIMARY_NODE_LABEL)
            .add_property("id", uri_to_node_id(interchange_node.uri))
            .set_variable("subject")
            .build()
        )
        for interchange_relationship in interchange_node.relationships:
            interchange_relationship_object = interchange_relationship.object
            interchange_relationship_objects.add(interchange_relationship_object)

            object_node_pattern: NodePattern = (
                NodePattern.builder()
                .add_label(_PRIMARY_NODE_LABEL)
                .add_property("id", uri_to_node_id(interchange_relationship_object))
                .set_variable("object")
                .build()
            )

            create_relationship_statement_builder = (
                cypher.CreateRelationshipStatement.builder(
                    label=uri_to_relationship_label(interchange_relationship.predicate),
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
                assert isinstance(property_value, cypher.PropertyValue)
                create_relationship_statement_builder.add_property(
                    interchange_node_property_name, property_value
                )

            yield create_relationship_statement_builder.build()
