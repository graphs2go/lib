from collections.abc import Iterable

from rdflib import SKOS

from graphs2go.models import interchange, skos
from graphs2go.transformers.transform_interchange_graph import (
    transform_interchange_graph,
)


def _transform_interchange_labels_to_skos_labels(
    interchange_node: interchange.Node,
    subject_skos_model_builder: skos.LabeledModel.Builder,
) -> Iterable[skos.Label]:
    for interchange_label in interchange_node.labels:
        if interchange_label.type is None:
            continue

        subject_skos_model_builder.add_lexical_label(
            label=interchange_label.literal_form, type_=interchange_label.type
        )

        skos_label = (
            skos.Label.builder(
                literal_form=interchange_label.literal_form,
                uri=interchange_label.uri,
            )
            .set_created(interchange_label.created)
            .set_modified(interchange_label.modified)
            .build()
        )
        yield skos_label

        subject_skos_model_builder.add_lexical_label(
            label=skos_label, type_=interchange_label.type
        )


def _transform_skos_concept_interchange_node_to_skos_models(
    interchange_node: interchange.Node,
) -> Iterable[skos.Model]:
    skos_concept_builder = (
        skos.Concept.builder(uri=interchange_node.uri)  # type: ignore
        .set_created(interchange_node.created)
        .set_modified(interchange_node.modified)
    )

    yield from _transform_interchange_labels_to_skos_labels(
        interchange_node, skos_concept_builder
    )

    # Interchange properties with predicates that are skos:note sub-properties
    for interchange_property in interchange_node.properties:
        if interchange_property.predicate == SKOS.notation:
            skos_concept_builder.add_notation(interchange_property.object)
        elif interchange_property.predicate in skos.Concept.NOTE_PREDICATES:
            skos_concept_builder.add_note(
                interchange_property.predicate, interchange_property.object
            )

    # Interchange relationships between concepts -> SKOS semantic relations
    for interchange_relationship in interchange_node.relationships:
        if interchange_relationship.predicate == SKOS.inScheme:
            skos_concept_builder.add_in_scheme(interchange_relationship.object)
        elif (
            interchange_relationship.predicate
            in skos.Concept.SEMANTIC_RELATION_PREDICATES
        ):
            skos_concept_builder.add_semantic_relation(
                interchange_relationship.predicate,
                interchange_relationship.object,
            )

    yield skos_concept_builder.build()


def _transform_skos_concept_scheme_interchange_node_to_skos_models(
    interchange_node: interchange.Node,
) -> Iterable[skos.Model]:
    skos_concept_scheme_builder = (
        skos.ConceptScheme.builder(uri=interchange_node.uri)  # type: ignore
        .set_created(interchange_node.created)
        .set_modified(interchange_node.modified)
    )

    yield from _transform_interchange_labels_to_skos_labels(
        interchange_node, skos_concept_scheme_builder
    )

    yield skos_concept_scheme_builder.build()


def transform_interchange_graph_to_skos_models(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
) -> Iterable[skos.Model]:
    yield from transform_interchange_graph(
        in_process=True,
        interchange_graph_descriptor=interchange_graph_descriptor,
        interchange_node_rdf_type=SKOS.ConceptScheme,
        transform_interchange_node=_transform_skos_concept_scheme_interchange_node_to_skos_models,
    )

    yield from transform_interchange_graph(
        interchange_graph_descriptor=interchange_graph_descriptor,
        interchange_node_rdf_type=SKOS.Concept,
        transform_interchange_node=_transform_skos_concept_interchange_node_to_skos_models,
    )
