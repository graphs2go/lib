import itertools
from collections.abc import Iterable
from pathlib import Path

import pytest
from returns.maybe import Some

from graphs2go.models import interchange, rdf, skos, LabelType
from graphs2go.namespaces import SKOS
from graphs2go.resources.rdf_store_config import RdfStoreConfig
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.stores.rdf import QuadStore
from graphs2go.stores.skos import ModelStore as SkosModelStore
from graphs2go.utils.uuid_urn import uuid_urn


@pytest.fixture()
def interchange_model_store(
    interchange_model_store_descriptor: InterchangeModelStore.Descriptor,
) -> Iterable[InterchangeModelStore]:
    with InterchangeModelStore.open(
        interchange_model_store_descriptor, read_only=True
    ) as interchange_model_store:
        yield interchange_model_store


@pytest.fixture()
def interchange_model_store_descriptor(
    rdf_store_config: RdfStoreConfig,
) -> InterchangeModelStore.Descriptor:
    interchange_model_store_identifier = uuid_urn()
    with InterchangeModelStore(
        identifier=interchange_model_store_identifier,
        quad_store=QuadStore.create(
            config=rdf_store_config,
            identifier=interchange_model_store_identifier,
        ),
    ) as store:
        concept_scheme = (
            interchange.Node.builder(iri=uuid_urn())
            .add_type(SKOS.ConceptScheme)
            .build()
        )
        store.add(concept_scheme)
        store.add(
            interchange.Label.builder(
                literal_form=rdf.Literal("label"),
                subject=concept_scheme,
                type_=Some(LabelType.PREFERRED),
            ).build()
        )

        concepts = tuple(
            interchange.Node.builder(iri=uuid_urn()).add_type(SKOS.Concept).build()
            for _ in range(2)
        )
        for concept_i, concept in enumerate(concepts):
            store.add(concept)

            store.add(
                interchange.Label.builder(
                    literal_form=rdf.Literal("label" + str(concept_i + 1)),
                    subject=concept,
                    type_=Some(LabelType.PREFERRED),
                ).build()
            )

            store.add(
                interchange.Property.builder(
                    subject=concept,
                    predicate=SKOS.definition,
                    object_=rdf.Literal("definition" + str(concept_i + 1)),
                ).build()
            )

            store.add(
                interchange.Relationship.builder(
                    object_=concept_scheme,
                    predicate=SKOS.inScheme,
                    subject=concept,
                ).build()
            )

        for concept1, concept2 in itertools.combinations(concepts, 2):
            store.add(
                interchange.Relationship.builder(
                    subject=concept1.iri, predicate=SKOS.broader, object_=concept2.iri
                ).build()
            )

        return store.descriptor


@pytest.fixture()
def interchange_label(interchange_node: interchange.Node) -> interchange.Label:
    return next(iter(interchange_node.labels()))


@pytest.fixture()
def interchange_node(
    interchange_model_store: InterchangeModelStore,
) -> interchange.Node:
    for node in interchange_model_store.nodes():
        return node
    pytest.fail("no nodes")


@pytest.fixture()
def interchange_property(
    interchange_model_store: InterchangeModelStore,
) -> interchange.Property:
    for node in interchange_model_store.nodes():
        for property_ in node.properties():
            return property_
    pytest.fail("no properties")


@pytest.fixture()
def interchange_relationship(
    interchange_model_store: InterchangeModelStore,
) -> interchange.Relationship:
    for node in interchange_model_store.nodes():
        for relationship in node.relationships():
            return relationship
    pytest.fail("no relationships")


@pytest.fixture
def rdf_store_config(tmp_path: Path) -> RdfStoreConfig:
    return RdfStoreConfig.default(oxigraph_directory_path_default=Some(tmp_path))


@pytest.fixture(scope="session")
def skos_concept(skos_model_store: SkosModelStore) -> skos.Concept:
    for concept in skos_model_store.concepts():
        return concept
    pytest.fail("no concepts")


@pytest.fixture(scope="session")
def skos_concept_scheme(skos_model_store: SkosModelStore) -> skos.ConceptScheme:
    for concept_scheme in skos_model_store.concept_schemes():
        return concept_scheme
    pytest.fail("no concept schemes")


@pytest.fixture()
def skos_model_store(rdf_store_config: RdfStoreConfig) -> SkosModelStore:
    store_identifier = uuid_urn()
    store = SkosModelStore(
        identifier=store_identifier,
        quad_store=QuadStore.create(
            config=rdf_store_config, identifier=store_identifier
        ),
    )

    concept_scheme = skos.ConceptScheme.builder(iri=uuid_urn()).build()
    store.add(concept_scheme)

    concept_builders: list[skos.Concept.Builder] = []
    for _ in range(2):
        concept_builder = skos.Concept.builder(iri=uuid_urn())
        concept_builder.add_in_scheme(concept_scheme.iri)
        concept_builder.add_notation(rdf.Literal("testnotation"))
        concept_builder.add_note(SKOS.note, rdf.Literal("testnote"))

        label_i = 1
        for label_type in LabelType:
            label = skos.Label.builder(
                literal_form=rdf.Literal("label" + str(label_i)), iri=uuid_urn()
            ).build()
            store.add(label)
            concept_builder.add_lexical_label(label=label, type_=label_type)
            label_i += 1

            concept_builder.add_lexical_label(
                label=rdf.Literal("label" + str(label_i)), type_=label_type
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
        store.add(concept_builder.build())

    return store


@pytest.fixture(scope="session")
def skos_label(skos_model_store: SkosModelStore) -> skos.Label:
    for label in skos_model_store.labels():
        return label
    pytest.fail("no labels")
