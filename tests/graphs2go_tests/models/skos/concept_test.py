import pytest
from rdflib import Literal

from graphs2go.models import skos


def test_alt_label(skos_concept: skos.Concept) -> None:
    alt_labels = tuple(skos_concept.alt_label)
    assert len(alt_labels) == 2
    assert any(isinstance(alt_label, skos.Label) for alt_label in alt_labels)
    assert any(isinstance(alt_label, Literal) for alt_label in alt_labels)


def test_builder(skos_concept: skos.Concept) -> None:  # noqa: ARG001
    pass


def test_broader(skos_graph: skos.Graph) -> None:
    for concept in skos_graph.concepts:
        for broader_concept in concept.broader:
            assert isinstance(broader_concept, skos.Concept)
            assert broader_concept.uri in {
                concept.uri for concept in skos_graph.concepts
            }
            return
    pytest.fail("no broader")


def test_in_scheme(
    skos_concept: skos.Concept, skos_concept_scheme: skos.ConceptScheme
) -> None:
    in_schemes = tuple(skos_concept.in_scheme)
    assert len(in_schemes) == 1
    assert isinstance(in_schemes[0], skos.ConceptScheme)
    assert in_schemes[0].uri == skos_concept_scheme.uri


def test_pref_label(skos_concept: skos.Concept) -> None:
    pref_labels = tuple(skos_concept.pref_label)
    assert len(pref_labels) == 2
    assert any(isinstance(pref_label, skos.Label) for pref_label in pref_labels)
    assert any(isinstance(pref_label, Literal) for pref_label in pref_labels)
