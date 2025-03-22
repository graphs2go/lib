from graphs2go.stores.skos import ModelStore as SkosModelStore


def test_concepts(skos_model_store: SkosModelStore) -> None:
    concepts = tuple(skos_model_store.concepts())
    assert concepts


def test_concept_schemes(skos_model_store: SkosModelStore) -> None:
    concept_schemes = tuple(skos_model_store.concept_schemes())
    assert concept_schemes


def test_labels(skos_model_store: SkosModelStore) -> None:
    labels = tuple(skos_model_store.labels())
    assert labels
