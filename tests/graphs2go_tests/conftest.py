import itertools
import pytest
from rdflib import SKOS, Literal

from graphs2go.models import interchange, skos
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.utils.uuid_urn import uuid_urn


@pytest.fixture(scope="session")
def interchange_concept(
    interchange_graph: interchange.Graph,
) -> interchange.Concept:
    for concept in interchange_graph.concepts:
        return concept
    pytest.fail("no concepts")


@pytest.fixture(scope="session")
def interchange_concepts() -> tuple[interchange.Concept, ...]:
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
def interchange_label(interchange_concept: interchange.Concept) -> interchange.Label:
    return next(iter(interchange_concept.labels))


@pytest.fixture(scope="session")
def interchange_node(interchange_graph: interchange.Graph) -> interchange.Node:
    for node in interchange_graph.nodes:
        return node
    pytest.fail("no nodes")


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
def skos_concept(skos_graph: skos.Graph) -> skos.Concept:
    for concept in skos_graph.concepts:
        return concept
    pytest.fail("no concepts")


@pytest.fixture(scope="session")
def skos_concept_scheme(skos_graph: skos.Graph) -> skos.ConceptScheme:
    for concept_scheme in skos_graph.concept_schemes:
        return concept_scheme
    pytest.fail("no concept schemes")


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


@pytest.fixture(scope="session")
def skos_label(skos_graph: skos.Graph) -> skos.Label:
    for label in skos_graph.labels:
        return label
    pytest.fail("no labels")
