from rdflib import Literal, URIRef
from rdflib.resource import Resource
from graphs2go.models import interchange, skos
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.transformers.transform_interchange_graph_to_skos_models import (
    transform_interchange_graph_to_skos_models,
)


def test_transform(interchange_graph: interchange.Graph) -> None:
    skos_graph = skos.Graph(rdf_store=MemoryRdfStore())
    for skos_model in transform_interchange_graph_to_skos_models(interchange_graph):
        skos_graph.add(skos_model)

    skos_concepts_by_uri = {concept.uri: concept for concept in skos_graph.concepts}

    for interchange_concept in interchange_graph.concepts:
        skos_concept = skos_concepts_by_uri[interchange_concept.uri]

        skos_alt_labels = tuple(skos_concept.alt_label)
        skos_pref_labels = tuple(skos_concept.pref_label)

        def assert_equivalent_skos_labels(
            interchange_label: interchange.Label,
            skos_labels: tuple[skos.Label | Literal, ...],
        ) -> None:
            expected_literal_form = interchange_label.literal_form
            assert any(
                True
                for skos_label_ in skos_labels
                if isinstance(skos_label_, Literal)
                and skos_label_ == expected_literal_form
            )
            assert any(
                True
                for skos_label_ in skos_labels
                if isinstance(skos_label_, skos.Label)
                and skos_label_.literal_form == expected_literal_form
            )

        for interchange_label in interchange_concept.labels:
            if interchange_label.type == interchange.Label.Type.ALTERNATIVE:
                assert_equivalent_skos_labels(interchange_label, skos_alt_labels)
            elif interchange_label.type == interchange.Label.Type.PREFERRED:
                assert_equivalent_skos_labels(interchange_label, skos_pref_labels)
            else:
                raise NotImplementedError(str(interchange_label.type))

        for interchange_relationship in interchange_concept.relationships:
            other_skos_concept_resource = skos_concept.resource.value(
                p=interchange_relationship.predicate
            )
            assert isinstance(other_skos_concept_resource, Resource)
            other_skos_concept_uri = other_skos_concept_resource.identifier
            assert isinstance(other_skos_concept_uri, URIRef)
            assert other_skos_concept_uri in skos_concepts_by_uri
