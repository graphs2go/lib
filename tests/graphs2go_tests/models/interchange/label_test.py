from graphs2go.models import interchange, rdf


def test_builder(interchange_label: interchange.Label) -> None:
    pass


def test_literal_form(interchange_label: interchange.Label) -> None:
    assert isinstance(interchange_label.literal_form, rdf.Literal)
