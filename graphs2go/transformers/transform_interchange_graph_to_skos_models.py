from collections.abc import Iterable

from rdflib import SKOS

from graphs2go.models import interchange, skos


def transform_interchange_graph_to_skos_models(
    interchange_graph: interchange.Graph,
) -> Iterable[skos.Model]:
    # Outer loop: interchange nodes with rdf:type skos:Concept or skos:ConceptScheme
    for interchange_node_rdf_type, skos_model_class in (
        (SKOS.Concept, skos.Concept),
        (SKOS.ConceptScheme, skos.ConceptScheme),
    ):
        for interchange_node in interchange_graph.nodes(
            rdf_type=interchange_node_rdf_type
        ):
            skos_model_builder: skos.Concept.Builder | skos.ConceptScheme.Builder = (
                skos_model_class.builder(uri=interchange_node.uri)  # type: ignore
                .set_created(interchange_node.created)
                .set_modified(interchange_node.modified)
            )

            # Interchange label -> SKOS label
            for interchange_label in interchange_node.labels:
                if interchange_label.type is None:
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

            # Interchange relationships between concepts -> SKOS semantic relations
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
