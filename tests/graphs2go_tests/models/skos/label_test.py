from graphs2go.models import rdf, skos


def test_builder(skos_label: skos.Label) -> None:
    pass


def test_literal_form(skos_label: skos.Label) -> None:
    assert isinstance(skos_label.literal_form, rdf.Literal)
