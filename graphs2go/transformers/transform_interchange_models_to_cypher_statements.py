from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

import stringcase
from returns.pipeline import is_successful

from graphs2go.models import cypher, interchange, rdf
from graphs2go.models.cypher.node_pattern import NodePattern
from graphs2go.namespaces import NAMESPACE_PREFIXES
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.transformers.transform_interchange_models import (
    transform_interchange_models,
)
from returns.maybe import Maybe, Nothing

if TYPE_CHECKING:
    from datetime import datetime


_PRIMARY_NODE_LABEL = "Node"


@dataclass(frozen=True)
class _OutputModel:
    cypher_statements: tuple[cypher.Statement, ...]
    interchange_node_iri: rdf.Iri
    interchange_relationship_objects: frozenset[rdf.Iri]


class _IriTransformer:
    def __init__(self, rdf_namespace_prefixes: rdf.NamespacePrefixes):
        from rdflib import Graph
        from rdflib.namespace import Namespace, NamespaceManager

        self.__namespace_manager = NamespaceManager(graph=Graph())
        for prefix, namespace in rdf_namespace_prefixes.items():
            self.__namespace_manager.bind(prefix, Namespace(namespace))

    def iri_to_curie(self, iri: rdf.Iri) -> tuple[str, str]:
        curie_parts = self.__namespace_manager.curie(iri).split(":", 1)
        assert len(curie_parts) == 2
        return curie_parts[0], curie_parts[1]

    def iri_to_node_id(self, iri: rdf.Iri) -> str:
        return str(iri)

    def iri_to_node_label(self, iri: rdf.Iri) -> str:
        curie = self.iri_to_curie(iri)
        return curie[0].capitalize() + stringcase.pascalcase(curie[1])

    def iri_to_property_name(self, iri: rdf.Iri) -> str:
        curie = self.iri_to_curie(iri)
        return curie[0].lower() + "_" + stringcase.snakecase(curie[1]).lower()

    def iri_to_relationship_label(self, iri: rdf.Iri) -> str:
        curie = self.iri_to_curie(iri)
        return curie[0].upper() + "_" + stringcase.snakecase(curie[1]).upper()


def _transform_interchange_node(
    rdf_namespace_prefixes: rdf.NamespacePrefixes, interchange_node: interchange.Node
) -> Iterable[_OutputModel]:
    cypher_statements: list[cypher.Statement] = []
    iri_transformer = _IriTransformer(rdf_namespace_prefixes=rdf_namespace_prefixes)

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
    interchange_relationship_objects: set[rdf.Iri] = set()
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


def transform_interchange_models_to_cypher_statements(
    interchange_model_store_descriptor: InterchangeModelStore.Descriptor,
    in_process: bool = False,
    rdf_namespace_prefixes: Maybe[rdf.NamespacePrefixes] = Nothing,
) -> Iterable[cypher.Statement]:
    interchange_node_iris: set[rdf.Iri] = set()
    interchange_relationship_objects: set[rdf.Iri] = set()

    output_model: _OutputModel
    for output_model in transform_interchange_models(
        interchange_model_store_descriptor=interchange_model_store_descriptor,
        transform_interchange_node=partial(
            _transform_interchange_node,
            rdf_namespace_prefixes.value_or(NAMESPACE_PREFIXES),
        ),
        in_process=in_process,
    ):
        interchange_node_iris.add(output_model.interchange_node_iri)  # type: ignore
        for (
            interchange_relationship_object
        ) in output_model.interchange_relationship_objects:  # type: ignore
            interchange_relationship_objects.add(interchange_relationship_object)

        yield from output_model.cypher_statements  # type: ignore

    # Interchange relationship objects that don't refer to interchange nodes should also be represented in the graph.
    iri_transformer = _IriTransformer(
        rdf_namespace_prefixes=rdf_namespace_prefixes.value_or(NAMESPACE_PREFIXES)
    )

    for external_interchange_relation_object in (
        interchange_relationship_objects - interchange_node_iris
    ):
        yield cypher.CreateNodeStatement.builder(
            id_=iri_transformer.iri_to_node_id(external_interchange_relation_object),
            label=_PRIMARY_NODE_LABEL,
        ).build()
