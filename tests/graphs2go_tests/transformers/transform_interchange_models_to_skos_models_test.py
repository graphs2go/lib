from typing import TYPE_CHECKING

from graphs2go.models import interchange, rdf, skos
from graphs2go.namespaces import SKOS
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.stores.rdf import QuadStore
from graphs2go.stores.skos import ModelStore as SkosModelStore
from graphs2go.transformers.transform_interchange_models_to_skos_models import (
    transform_interchange_models_to_skos_models,
)

if TYPE_CHECKING:
    from graphs2go.models.label_type import LabelType


def test_transform(
    interchange_model_store_descriptor: InterchangeModelStore.Descriptor,
    quad_store: QuadStore,
) -> None:
    with SkosModelStore(
        quad_store=quad_store,
    ) as skos_model_store:
        skos_model_store.add_all(
            transform_interchange_models_to_skos_models(
                interchange_model_store_descriptor
            )
        )

        skos_concept_schemes_by_iri = {
            concept_scheme.iri: concept_scheme
            for concept_scheme in skos_model_store.concept_schemes()
        }
        assert len(skos_concept_schemes_by_iri) == 1
        concept_scheme = next(iter(skos_concept_schemes_by_iri.values()))

        skos_concepts_by_iri = {
            concept.iri: concept for concept in skos_model_store.concepts()
        }

        with InterchangeModelStore.open(
            interchange_model_store_descriptor, read_only=True
        ) as interchange_model_store:
            for interchange_node in interchange_model_store.nodes_by_type(SKOS.Concept):
                skos_concept = skos_concepts_by_iri[interchange_node.iri]

                skos_lexical_labels_by_type: dict[
                    LabelType | None, list[rdf.Literal | skos.Label | rdf.Iri]
                ] = {}
                for label_type, skos_lexical_label in skos_concept.lexical_labels():
                    skos_lexical_labels_by_type.setdefault(label_type, []).append(
                        skos_lexical_label
                    )

                for interchange_label in interchange_node.labels():
                    assert any(
                        True
                        for skos_lexical_label in skos_lexical_labels_by_type[
                            interchange_label.type.unwrap()
                        ]
                        if isinstance(skos_lexical_label, rdf.Literal)
                        and skos_lexical_label == interchange_label.literal_form
                    )
                    # assert any(
                    #     True
                    #     for skos_lexical_label in skos_lexical_labels_by_type[
                    #         interchange_label.type.unwrap()
                    #     ]
                    #     if isinstance(skos_lexical_label, skos.Label)
                    #     and skos_lexical_label.literal_form
                    #     == interchange_label.literal_form
                    # )

                for interchange_property in interchange_node.properties():
                    assert (
                        interchange_property.predicate == SKOS.notation
                        or interchange_property.predicate
                        in skos.Concept.NOTE_PREDICATES
                    )
                    assert isinstance(interchange_property.object_, rdf.Literal)

                for interchange_relationship in interchange_node.relationships():
                    other_resource: rdf.NamedResource = (
                        skos_concept.resource.value(interchange_relationship.predicate)
                        .unwrap()
                        .to_named_resource()
                        .unwrap()
                    )
                    other_iri = other_resource.iri
                    if interchange_relationship.predicate == SKOS.inScheme:
                        assert other_iri == concept_scheme.iri
                    else:
                        assert (
                            interchange_relationship.predicate
                            in skos.Concept.SEMANTIC_RELATION_PREDICATES
                        )
                        assert other_iri in skos_concepts_by_iri
