import pytest
from rdflib import Literal

from graphs2go.models import skos
from graphs2go.models.label_type import LabelType


def test_lexical_labels(skos_concept: skos.Concept) -> None:
    lexical_labels = tuple(skos_concept.lexical_labels)
    assert len(lexical_labels) == 6
    for label_type in LabelType:
        assert (
            sum(
                1
                for label_type_, lexical_label in lexical_labels
                if label_type == label_type_ and isinstance(lexical_label, skos.Label)
            )
            == 1
        )
        assert (
            sum(
                1
                for label_type_, lexical_label in lexical_labels
                if label_type == label_type_ and isinstance(lexical_label, Literal)
            )
            == 1
        )


def test_builder(skos_concept: skos.Concept) -> None:  # noqa: ARG001
    pass


def test_in_scheme(
    skos_concept: skos.Concept, skos_concept_scheme: skos.ConceptScheme
) -> None:
    in_schemes = tuple(skos_concept.in_scheme)
    assert len(in_schemes) == 1
    assert isinstance(in_schemes[0], skos.ConceptScheme)
    assert in_schemes[0].uri == skos_concept_scheme.uri


def test_semantic_relations(skos_graph: skos.Graph) -> None:
    for concept in skos_graph.concepts:
        for predicate, related_concept in concept.semantic_relations:
            assert predicate in skos.Concept.SEMANTIC_RELATION_PREDICATES
            assert isinstance(related_concept, skos.Concept)
            assert related_concept.uri in {
                concept.uri for concept in skos_graph.concepts
            }
            return
    pytest.fail("no semantic relations")
