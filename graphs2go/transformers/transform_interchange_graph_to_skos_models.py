from collections.abc import Iterable

from dagster import get_dagster_logger
from rdflib import SKOS

from graphs2go.models import interchange, skos


def transform_interchange_graph_to_skos_models(
    interchange_graph: interchange.Graph,
) -> Iterable[skos.Model]:
    logger = get_dagster_logger()

    for interchange_concept in interchange_graph.concepts:
        skos_concept_builder = skos.Concept.builder(uri=interchange_concept.uri)

        for interchange_label in interchange_concept.labels:
            if interchange_label.type == interchange.Label.Type.ALTERNATIVE:
                skos_concept_builder.add_alt_label(interchange_label.literal_form)
                skos_label = skos.Label.builder(
                    literal_form=interchange_label.literal_form,
                    uri=interchange_label.uri,
                ).build()
                yield skos_label
                skos_concept_builder.add_alt_label(skos_label)
            elif interchange_label.type == interchange.Label.Type.PREFERRED:
                skos_concept_builder.add_pref_label(interchange_label.literal_form)
                skos_label = skos.Label.builder(
                    literal_form=interchange_label.literal_form,
                    uri=interchange_label.uri,
                ).build()
                yield skos_label
                skos_concept_builder.add_pref_label(skos_label)
            else:
                logger.warning(
                    "interchange concept %s has non-SKOS label %s",
                    interchange_concept.uri,
                    interchange_label.uri,
                )
                continue

        for interchange_relationship in interchange_concept.relationships:
            if interchange_relationship.predicate.startswith(SKOS._NS):  # noqa: SLF001
                skos_concept_builder.add_relationship(
                    object_=interchange_relationship.object,
                    predicate=interchange_relationship.predicate,
                )

        yield skos_concept_builder.build()
