from collections.abc import Iterable

from returns.pipeline import is_successful

from graphs2go.models import interchange, rdf
from graphs2go.namespaces import RDF, RDFS
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.transformers.transform_interchange_models import (
    transform_interchange_models,
)


def _transform_interchange_node_to_direct_rdf_models(
    interchange_node: interchange.Node,
) -> Iterable[rdf.NamedModel]:
    rdf_resource_builder = rdf.NamedResource.builder(iri=interchange_node.iri)

    for interchange_label in interchange_node.labels():
        if is_successful(interchange_label.type):
            rdf_resource_builder.add(
                interchange_label.type.unwrap().skos_predicate,
                interchange_label.literal_form,
            )
        else:
            rdf_resource_builder.add(RDFS.label, interchange_label.literal_form)

    for interchange_property in interchange_node.properties():
        rdf_resource_builder.add(
            interchange_property.predicate, interchange_property.object
        )

    for interchange_relationship in interchange_node.relationships():
        rdf_resource_builder.add(
            interchange_relationship.predicate, interchange_relationship.object
        )

    for type_iri in interchange_node.types:
        rdf_resource_builder.add(RDF.type, type_iri)

    yield rdf.NamedModel(rdf_resource_builder.build())


def transform_interchange_models_to_direct_rdf_models(
    interchange_model_store_descriptor: InterchangeModelStore.Descriptor,
    in_process: bool = False,
) -> Iterable[rdf.NamedModel]:
    """
    Transform the interchange graph into a "direct" RDF representation, one with only as much reification as it
    needs to express the nodes, relationships, and properties in the interchange graph.

    "Direct" is used in the Wikidata sense of "direct claim".
    https://lists.wikimedia.org/hyperkitty/list/wikidata@lists.wikimedia.org/message/5YFA5QB7FCT2KIONGZX6GOTT4URHQRVJ/
    """

    yield from transform_interchange_models(
        in_process=in_process,
        interchange_model_store_descriptor=interchange_model_store_descriptor,
        transform_interchange_node=_transform_interchange_node_to_direct_rdf_models,
    )
