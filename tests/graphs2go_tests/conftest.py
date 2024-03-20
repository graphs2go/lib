import itertools
import pytest
from rdflib import SKOS, Literal

from graphs2go.models import interchange, skos
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.utils.uuid_urn import uuid_urn


@pytest.fixture(scope="session")
def interchange_concept_label(
    interchange_concept_labels: tuple[interchange.Label, interchange.Label]
) -> interchange.Label:
    return interchange_concept_labels[0]


@pytest.fixture(scope="session")
def interchange_concept_labels(
    interchange_concepts: tuple[interchange.Concept, ...]
) -> tuple[interchange.Label, ...]:
    labels: list[interchange.Label] = []
    for concept in interchange_concepts:
        concept_labels = tuple(concept.labels)
        assert len(concept_labels) == 1
        labels.extend(concept_labels)
    return tuple(labels)


@pytest.fixture(scope="session")
def interchange_concept(
    interchange_concepts: tuple[interchange.Concept, ...]
) -> interchange.Concept:
    return interchange_concepts[0]


@pytest.fixture(scope="session")
def interchange_concepts(
    interchange_graph: interchange.Graph,
) -> tuple[interchange.Concept, ...]:
    concepts = tuple(interchange_graph.concepts)
    assert concepts
    return concepts


@pytest.fixture(scope="session")
def interchange_graph() -> interchange.Graph:
    graph = interchange.Graph(rdf_store=MemoryRdfStore())

    concepts = tuple(
        interchange.Concept.builder(uri=uuid_urn()).build() for _ in range(2)
    )
    for concept_i, concept in enumerate(concepts):
        graph.add(concept)

        graph.add(
            interchange.Label.builder(
                literal_form=Literal("label" + str(concept_i + 1)),
                predicate=SKOS.prefLabel,
                subject=concept.uri,
            ).build()
        )

        graph.add(
            interchange.Property.builder(
                subject=concept.uri,
                predicate=SKOS.definition,
                object_=Literal("definition" + str(concept_i + 1)),
            ).build()
        )

    for concept1, concept2 in itertools.combinations(concepts, 2):
        graph.add(
            interchange.Relationship.builder(
                subject=concept1.uri, predicate=SKOS.broader, object_=concept2.uri
            ).build()
        )

    return graph


@pytest.fixture(scope="session")
def interchange_label(
    interchange_concept_label: interchange.Label,
) -> interchange.Label:
    return interchange_concept_label


@pytest.fixture(scope="session")
def interchange_node(interchange_concept: interchange.Concept) -> interchange.Node:
    return interchange_concept


@pytest.fixture(scope="session")
def interchange_property(interchange_graph: interchange.Graph) -> interchange.Property:
    for concept in interchange_graph.concepts:
        for property_ in concept.properties:
            return property_
    pytest.fail("no properties")


@pytest.fixture(scope="session")
def interchange_relationship(
    interchange_graph: interchange.Graph,
) -> interchange.Relationship:
    for concept in interchange_graph.concepts:
        for relationship in concept.relationships:
            return relationship
    pytest.fail("no relationships")


@pytest.fixture(scope="session")
def skos_graph() -> skos.Graph:
    graph = skos.Graph(rdf_store=MemoryRdfStore())

    concept_builders: list[skos.Concept.Builder] = []
    for concept_i in range(2):
        concept_builder = skos.Concept.builder(uri=uuid_urn())

        concept_builder.add_alt_label(
            skos.Label.builder(
                literal_form=Literal("altLabel" + str(concept_i + 1)), uri=uuid_urn()
            ).build()
        )

        concept_builder.add_pref_label(
            skos.Label.builder(
                literal_form=Literal("prefLabel" + str(concept_i + 1)), uri=uuid_urn()
            ).build()
        )

        concept_builders.append(concept_builder)

    for concept_builder_1, concept_builder_2 in itertools.combinations(
        concept_builders, 2
    ):
        concept_builder_1.add_broader(concept_builder_2.build())

    for concept_builder in concept_builders:
        graph.add(concept_builder.build())

    return graph
