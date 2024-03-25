from collections.abc import Iterable
from datetime import datetime, date

import stringcase
from dagster import get_dagster_logger
from rdflib import URIRef, Graph
from rdflib.namespace import NamespaceManager

from graphs2go.models import interchange, cypher


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

    for interchange_node in interchange_graph.nodes():
        interchange_node_secondary_rdf_types = tuple(
            interchange_node.secondary_rdf_types
        )
        create_node_statement_builder = cypher.CreateNodeStatement.builder(
            id_=uri_to_node_id(interchange_node.uri),
            label=(
                uri_to_node_label(interchange_node_secondary_rdf_types[0])
                if interchange_node_secondary_rdf_types
                else "NODE"
            ),
        )

        for interchange_node_secondary_rdf_type in interchange_node_secondary_rdf_types[
            1:
        ]:
            create_node_statement_builder.add_label(
                uri_to_node_label(interchange_node_secondary_rdf_type)
            )

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

            create_node_statement_builder.add_property(
                uri_to_property_name(interchange_property.predicate), property_value
            )

        yield create_node_statement_builder.build()
