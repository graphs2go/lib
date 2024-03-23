from collections.abc import Iterable

from dagster import get_dagster_logger
from rdflib import SKOS

from graphs2go.models import interchange, skos


def transform_interchange_graph_to_skos_models(
    interchange_graph: interchange.Graph,
) -> Iterable[skos.Model]:
    logger = get_dagster_logger()

    for interchange_node_rdf_type, skos_model_class in (
        (SKOS.Concept, skos.Concept),
        (SKOS.ConceptScheme, skos.ConceptScheme),
    ):
        for interchange_node in interchange_graph.nodes(
            rdf_type=interchange_node_rdf_type
        ):
            skos_model_builder: skos.LabeledModel.Builder = (
                skos_model_class.builder(uri=interchange_node.uri)
                .set_created(interchange_node.created)
                .set_modified(interchange_node.modified)
            )

            for interchange_label in interchange_node.labels:
                if interchange_label.type not in {
                    interchange.Label.Type.ALTERNATIVE,
                    interchange_label.Type.PREFERRED,
                }:
                    logger.warning(
                        "interchange concept %s has non-SKOS label %s",
                        interchange_node.uri,
                        interchange_label.uri,
                    )
                    continue

                skos_model_builder.add_lexical_label(
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
                skos_model_builder.add_lexical_label(
                    label=skos_label, type_=interchange_label.type
                )

            if isinstance(skos_model_builder, skos.Concept.Builder):
                for interchange_relationship in interchange_node.relationships:
                    if interchange_relationship.predicate == SKOS.inScheme:
                        skos_model_builder.add_in_scheme(
                            interchange_relationship.object
                        )
                    elif (
                        interchange_relationship.predicate
                        in skos.Concept.SEMANTIC_RELATION_PREDICATES
                    ):
                        skos_model_builder.add_semantic_relation(
                            object_=interchange_relationship.object,
                            predicate=interchange_relationship.predicate,
                        )

            yield skos_model_builder.build()
