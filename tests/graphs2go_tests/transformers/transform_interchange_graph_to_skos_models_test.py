from rdflib import SKOS, Literal, URIRef
from rdflib.resource import Resource

from graphs2go.models import interchange, skos
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.transformers.transform_interchange_graph_to_skos_models import (
    transform_interchange_graph_to_skos_models,
)


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

        for interchange_label in interchange_node.labels:
            if interchange_label.type == interchange.Label.Type.ALTERNATIVE:
                assert_equivalent_skos_labels(interchange_label, skos_alt_labels)
            elif interchange_label.type == interchange.Label.Type.PREFERRED:
                assert_equivalent_skos_labels(interchange_label, skos_pref_labels)
            else:
                raise NotImplementedError(str(interchange_label.type))

        for interchange_relationship in interchange_node.relationships:
            other_resource = skos_concept.resource.value(
                p=interchange_relationship.predicate
            )
            assert isinstance(other_resource, Resource)
            other_uri = other_resource.identifier
            assert isinstance(other_uri, URIRef)
            assert other_uri in skos_concepts_by_uri or other_uri == concept_scheme.uri
