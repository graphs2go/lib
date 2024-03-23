import itertools

import pytest
from rdflib import SKOS, Literal

from graphs2go.models import interchange, skos
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.utils.uuid_urn import uuid_urn


@pytest.fixture(scope="session")
def interchange_graph() -> interchange.Graph:
    graph = interchange.Graph(identifier=uuid_urn(), rdf_store=MemoryRdfStore())

    concept_scheme = (
        interchange.Node.builder(uri=uuid_urn())
        .add_rdf_type(SKOS.ConceptScheme)
        .build()
    )
    graph.add(concept_scheme)
    graph.add(
        interchange.Label.builder(
            literal_form=Literal("label"),
            subject=concept_scheme,
            type_=interchange.Label.Type.PREFERRED,
        ).build()
    )

    concepts = tuple(
        interchange.Node.builder(uri=uuid_urn()).add_rdf_type(SKOS.Concept).build()
        for _ in range(2)
    )
    for concept_i, concept in enumerate(concepts):
        graph.add(concept)

        graph.add(
            interchange.Label.builder(
                literal_form=Literal("label" + str(concept_i + 1)),
                subject=concept,
                type_=interchange.Label.Type.PREFERRED,
            ).build()
        )

        graph.add(
            interchange.Property.builder(
                subject=concept,
                predicate=SKOS.definition,
                object_=Literal("definition" + str(concept_i + 1)),
            ).build()
        )

        graph.add(
            interchange.Relationship.builder(
                object_=concept_scheme,
                predicate=SKOS.inScheme,
                subject=concept,
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
def interchange_label(interchange_node: interchange.Node) -> interchange.Label:
    return next(iter(interchange_node.labels))


@pytest.fixture(scope="session")
def interchange_node(interchange_graph: interchange.Graph) -> interchange.Node:
    for node in interchange_graph.nodes():
        return node
    pytest.fail("no nodes")


@pytest.fixture(scope="session")
def interchange_property(interchange_graph: interchange.Graph) -> interchange.Property:
    for node in interchange_graph.nodes():
        for property_ in node.properties:
            return property_
    pytest.fail("no properties")


@pytest.fixture(scope="session")
def interchange_relationship(
    interchange_graph: interchange.Graph,
) -> interchange.Relationship:
    for node in interchange_graph.nodes():
        for relationship in node.relationships:
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
    graph = skos.Graph(identifier=uuid_urn(), rdf_store=MemoryRdfStore())

    concept_scheme = skos.ConceptScheme.builder(uri=uuid_urn()).build()
    graph.add(concept_scheme)

    concept_builders: list[skos.Concept.Builder] = []
    for concept_i in range(2):
        concept_builder = skos.Concept.builder(uri=uuid_urn())
        concept_builder.add_in_scheme(concept_scheme)

        alt_label = skos.Label.builder(
            literal_form=Literal("xlAltLabel" + str(concept_i + 1)), uri=uuid_urn()
        ).build()
        graph.add(alt_label)
        concept_builder.add_alt_label(alt_label)
        concept_builder.add_alt_label(Literal("altLabel" + str(concept_i + 1)))

        pref_label = skos.Label.builder(
            literal_form=Literal("xlPrefLabel" + str(concept_i + 1)), uri=uuid_urn()
        ).build()
        graph.add(pref_label)
        concept_builder.add_pref_label(pref_label)
        concept_builder.add_pref_label(Literal("prefLabel" + str(concept_i + 1)))

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
