from graphs2go.models import skos


def test_concepts(skos_graph: skos.Graph) -> None:
    concepts = tuple(skos_graph.concepts)
    assert concepts


def test_concept_schemes(skos_graph: skos.Graph) -> None:
    concept_schemes = tuple(skos_graph.concept_schemes)
    assert concept_schemes


def test_labels(skos_graph: skos.Graph) -> None:
    labels = tuple(skos_graph.labels)
    assert labels
