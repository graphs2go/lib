from rdflib import Literal

from graphs2go.models import skos


def test_builder(skos_label: skos.Label) -> None:
    pass


def test_literal_form(skos_label: skos.Label) -> None:
    assert isinstance(skos_label.literal_form, Literal)
