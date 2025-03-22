from graphs2go.models import interchange, rdf


def test_builder(
    interchange_property: interchange.Property,
) -> None:
    pass


def test_object(interchange_property: interchange.Property) -> None:
    assert isinstance(interchange_property.object, rdf.Literal)


def test_predicate(interchange_property: interchange.Property) -> None:
    assert isinstance(interchange_property.predicate, rdf.Iri)


def test_subject(
    interchange_model_store: InterchangeModelStore,
    interchange_property: interchange.Property,
) -> None:
    assert isinstance(interchange_property.subject, rdf.Iri)
    assert interchange_property.subject in {
        node.iri for node in interchange_model_store.nodes()
    }
