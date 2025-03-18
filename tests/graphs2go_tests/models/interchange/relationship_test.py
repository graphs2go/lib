from graphs2go.models import interchange, rdf


def test_builder(
    interchange_relationship: interchange.Relationship,
) -> None:
    pass


def test_object(
    interchange_graph: interchange.Graph,
    interchange_relationship: interchange.Relationship,
) -> None:
    assert isinstance(interchange_relationship.object, rdf.Iri)
    assert interchange_relationship.subject in {
        node.iri for node in interchange_graph.nodes()
    }


def test_predicate(interchange_relationship: interchange.Relationship) -> None:
    assert isinstance(interchange_relationship.predicate, rdf.Iri)


def test_subject(
    interchange_graph: interchange.Graph,
    interchange_relationship: interchange.Relationship,
) -> None:
    assert isinstance(interchange_relationship.subject, rdf.Iri)
    assert interchange_relationship.subject in {
        node.iri for node in interchange_graph.nodes()
    }
