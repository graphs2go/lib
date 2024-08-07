from collections.abc import Iterable

from rdflib import SKOS
from returns.maybe import Some
from returns.pipeline import is_successful

from graphs2go.models import interchange, skos
from graphs2go.transformers.transform_interchange_graph import (
    transform_interchange_graph,
)


def _transform_interchange_labels_to_skos_labels(
    interchange_labels: Iterable[interchange.Label],
    subject_skos_model_builder: skos.LabeledModel.Builder,
) -> Iterable[skos.Label]:
    for interchange_label in interchange_labels:
        if not is_successful(interchange_label.type):
            continue

        subject_skos_model_builder.add_lexical_label(
            label=interchange_label.literal_form,
            type_=interchange_label.type.unwrap(),
        )

        if not interchange_label.is_reified:
            continue

        skos_label = (
            skos.Label.builder(
                literal_form=interchange_label.literal_form,
                iri=interchange_label.iri,
            )
            .set_created(interchange_label.created.value_or(None))
            .set_modified(interchange_label.modified.value_or(None))
            .build()
        )
        yield skos_label

        subject_skos_model_builder.add_lexical_label(
            label=skos_label, type_=interchange_label.type.unwrap()
        )


def _transform_skos_concept_interchange_node_to_skos_models(
    interchange_node: interchange.Node,
) -> Iterable[skos.Model]:
    skos_concept_builder = (
        skos.Concept.builder(iri=interchange_node.iri)  # type: ignore
        .set_created(interchange_node.created.value_or(None))
        .set_modified(interchange_node.modified.value_or(None))
    )

    yield from _transform_interchange_labels_to_skos_labels(
        interchange_node.labels(), skos_concept_builder
    )

    # Interchange properties with predicates that are skos:note sub-properties
    for interchange_property in interchange_node.properties():
        if interchange_property.predicate == SKOS.notation:
            skos_concept_builder.add_notation(interchange_property.object)
        elif interchange_property.predicate in skos.Concept.NOTE_PREDICATES:
            skos_concept_builder.add_note(
                interchange_property.predicate, interchange_property.object
            )

    # Interchange relationships
    for interchange_relationship in interchange_node.relationships():
        if interchange_relationship.predicate == SKOS.inScheme:
            skos_concept_builder.add_in_scheme(interchange_relationship.object)
        elif interchange_relationship.predicate == SKOS.topConceptOf:
            skos_concept_builder.add_top_concept_of(interchange_relationship.object)
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
        skos.ConceptScheme.builder(iri=interchange_node.iri)  # type: ignore
        .set_created(interchange_node.created.value_or(None))
        .set_modified(interchange_node.modified.value_or(None))
    )

    yield from _transform_interchange_labels_to_skos_labels(
        interchange_node.labels(), skos_concept_scheme_builder
    )

    for interchange_relationship in interchange_node.relationships():
        if interchange_relationship.predicate == SKOS.hasTopConcept:
            skos_concept_scheme_builder.add_top_concept(interchange_relationship.object)

    yield skos_concept_scheme_builder.build()


def transform_interchange_graph_to_skos_models(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
) -> Iterable[skos.Model]:
    yield from transform_interchange_graph(
        in_process=True,
        interchange_graph_descriptor=interchange_graph_descriptor,
        interchange_node_type=Some(SKOS.ConceptScheme),
        transform_interchange_node=_transform_skos_concept_scheme_interchange_node_to_skos_models,
    )

    yield from transform_interchange_graph(
        interchange_graph_descriptor=interchange_graph_descriptor,
        interchange_node_type=Some(SKOS.Concept),
        transform_interchange_node=_transform_skos_concept_interchange_node_to_skos_models,
    )
