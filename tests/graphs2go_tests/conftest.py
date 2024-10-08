import itertools
from collections.abc import Iterable

import pytest
from rdflib import SKOS, Literal
from returns.maybe import Nothing, Some

from graphs2go.models import interchange, skos
from graphs2go.models.label_type import LabelType
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.rdf_stores.oxigraph_rdf_store import OxigraphRdfStore
from graphs2go.resources.rdf_store_config import RdfStoreConfig
from graphs2go.utils.uuid_urn import uuid_urn


@pytest.fixture()
def interchange_graph(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
) -> Iterable[interchange.Graph]:
    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        yield interchange_graph


@pytest.fixture()
def interchange_graph_descriptor() -> interchange.Graph.Descriptor:
    interchange_graph_identifier = uuid_urn()
    with interchange.Graph(
        identifier=interchange_graph_identifier,
        rdf_store=OxigraphRdfStore.create_(
            identifier=interchange_graph_identifier,
            rdf_store_config=RdfStoreConfig.default(directory_path_default=Nothing),
        ),
    ) as graph:
        concept_scheme = (
            interchange.Node.builder(iri=uuid_urn())
            .add_type(SKOS.ConceptScheme)
            .build()
        )
        graph.add(concept_scheme)
        graph.add(
            interchange.Label.builder(
                literal_form=Literal("label"),
                subject=concept_scheme,
                type_=Some(LabelType.PREFERRED),
            ).build()
        )

        concepts = tuple(
            interchange.Node.builder(iri=uuid_urn()).add_type(SKOS.Concept).build()
            for _ in range(2)
        )
        for concept_i, concept in enumerate(concepts):
            graph.add(concept)

            graph.add(
                interchange.Label.builder(
                    literal_form=Literal("label" + str(concept_i + 1)),
                    subject=concept,
                    type_=Some(LabelType.PREFERRED),
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
                    subject=concept1.iri, predicate=SKOS.broader, object_=concept2.iri
                ).build()
            )

        return graph.descriptor


@pytest.fixture()
def interchange_label(interchange_node: interchange.Node) -> interchange.Label:
    return next(iter(interchange_node.labels()))


@pytest.fixture()
def interchange_node(interchange_graph: interchange.Graph) -> interchange.Node:
    for node in interchange_graph.nodes():
        return node
    pytest.fail("no nodes")


@pytest.fixture()
def interchange_property(interchange_graph: interchange.Graph) -> interchange.Property:
    for node in interchange_graph.nodes():
        for property_ in node.properties():
            return property_
    pytest.fail("no properties")


@pytest.fixture()
def interchange_relationship(
    interchange_graph: interchange.Graph,
) -> interchange.Relationship:
    for node in interchange_graph.nodes():
        for relationship in node.relationships():
            return relationship
    pytest.fail("no relationships")


@pytest.fixture(scope="session")
def skos_concept(skos_graph: skos.Graph) -> skos.Concept:
    for concept in skos_graph.concepts():
        return concept
    pytest.fail("no concepts")


@pytest.fixture(scope="session")
def skos_concept_scheme(skos_graph: skos.Graph) -> skos.ConceptScheme:
    for concept_scheme in skos_graph.concept_schemes():
        return concept_scheme
    pytest.fail("no concept schemes")


@pytest.fixture(scope="session")
def skos_graph() -> skos.Graph:
    graph = skos.Graph(identifier=uuid_urn(), rdf_store=MemoryRdfStore())

    concept_scheme = skos.ConceptScheme.builder(iri=uuid_urn()).build()
    graph.add(concept_scheme)

    concept_builders: list[skos.Concept.Builder] = []
    for _ in range(2):
        concept_builder = skos.Concept.builder(iri=uuid_urn())
        concept_builder.add_in_scheme(concept_scheme.iri)
        concept_builder.add_notation(Literal("testnotation"))
        concept_builder.add_note(SKOS.note, Literal("testnote"))

        label_i = 1
        for label_type in LabelType:
            label = skos.Label.builder(
                literal_form=Literal("label" + str(label_i)), iri=uuid_urn()
            ).build()
            graph.add(label)
            concept_builder.add_lexical_label(label=label, type_=label_type)
            label_i += 1

            concept_builder.add_lexical_label(
                label=Literal("label" + str(label_i)), type_=label_type
            )
            label_i += 1

        concept_builders.append(concept_builder)

    for concept_builder_1, concept_builder_2 in itertools.combinations(
        concept_builders, 2
    ):
        concept_builder_1.add_semantic_relation(
            object_=concept_builder_2.build().iri, predicate=SKOS.broader
        )

    for concept_builder in concept_builders:
        graph.add(concept_builder.build())

    return graph


@pytest.fixture(scope="session")
def skos_label(skos_graph: skos.Graph) -> skos.Label:
    for label in skos_graph.labels():
        return label
    pytest.fail("no labels")
