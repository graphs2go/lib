from typing import TYPE_CHECKING

from rdflib import SKOS, Literal, URIRef
from rdflib.resource import Resource

from graphs2go.models import interchange, skos
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.transformers.transform_interchange_graph_to_skos_models import (
    transform_interchange_graph_to_skos_models,
)

if TYPE_CHECKING:
    from graphs2go.models.label_type import LabelType


def test_transform(interchange_graph: interchange.Graph) -> None:
    skos_graph = skos.Graph(
        identifier=interchange_graph.identifier, rdf_store=MemoryRdfStore()
    )
    skos_graph.add_all(transform_interchange_graph_to_skos_models(interchange_graph))

    skos_concept_schemes_by_uri = {
        concept_scheme.uri: concept_scheme
        for concept_scheme in skos_graph.concept_schemes
    }
    assert len(skos_concept_schemes_by_uri) == 1
    concept_scheme = next(iter(skos_concept_schemes_by_uri.values()))

    skos_concepts_by_uri = {concept.uri: concept for concept in skos_graph.concepts}

    for interchange_node in interchange_graph.nodes(rdf_type=SKOS.Concept):
        skos_concept = skos_concepts_by_uri[interchange_node.uri]

        skos_lexical_labels_by_type: dict[
            LabelType | None, list[Literal | skos.Label | URIRef]
        ] = {}
        for label_type, skos_lexical_label in skos_concept.lexical_labels:
            skos_lexical_labels_by_type.setdefault(label_type, []).append(
                skos_lexical_label
            )

        for interchange_label in interchange_node.labels:
            assert any(
                True
                for skos_lexical_label in skos_lexical_labels_by_type[
                    interchange_label.type
                ]
                if isinstance(skos_lexical_label, Literal)
                and skos_lexical_label == interchange_label.literal_form
            )
            assert any(
                True
                for skos_lexical_label in skos_lexical_labels_by_type[
                    interchange_label.type
                ]
                if isinstance(skos_lexical_label, skos.Label)
                and skos_lexical_label.literal_form == interchange_label.literal_form
            )

        for interchange_property in interchange_node.properties:
            assert (
                interchange_property.predicate == SKOS.notation
                or interchange_property.predicate in skos.Concept.NOTE_PREDICATES
            )
            assert isinstance(interchange_property.object, Literal)

        for interchange_relationship in interchange_node.relationships:
            other_resource = skos_concept.resource.value(
                p=interchange_relationship.predicate
            )
            assert isinstance(other_resource, Resource)
            other_uri = other_resource.identifier
            assert isinstance(other_uri, URIRef)
            if interchange_relationship.predicate == SKOS.inScheme:
                assert other_uri == concept_scheme.uri
            else:
                assert (
                    interchange_relationship.predicate
                    in skos.Concept.SEMANTIC_RELATION_PREDICATES
                )
                assert other_uri in skos_concepts_by_uri
