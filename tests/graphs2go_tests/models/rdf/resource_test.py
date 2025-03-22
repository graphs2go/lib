from datetime import date, datetime
from decimal import Decimal

import pytest

from graphs2go.models import rdf
from graphs2go.utils import uuid_urn
from graphs2go.namespaces import RDF


@pytest.fixture()
def builder(identifier: rdf.Resource.Identifier) -> rdf.Resource.Builder:
    return rdf.Resource.builder(identifier=identifier)


@pytest.fixture(scope="session")
def identifier() -> rdf.Resource.Identifier:
    return uuid_urn()


@pytest.fixture(scope="session")
def predicate() -> rdf.Quad_Predicate:
    return rdf.Iri("http://example.com/predicate")


def test_builder_add(builder: rdf.Resource.Builder) -> None:
    builder.add(RDF.type, RDF.Alt)
    builder.add(RDF.type, RDF.Bag)
    assert len(builder.build().dataset) == 2


def test_builder_build(builder: rdf.Resource.Builder) -> None:
    assert len(builder.build().dataset) == 0


def test_builder_set(builder: rdf.Resource.Builder) -> None:
    builder.add(RDF.type, RDF.Alt)
    builder.set(RDF.type, RDF.Bag)
    assert len(builder.build().dataset) == 1


def test_identifier(
    builder: rdf.Resource.Builder, identifier: rdf.Resource.Identifier
) -> None:
    assert builder.build().identifier == identifier


def test_value_to_blank_node(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = rdf.BlankNode()
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_blank_node()
        .unwrap()
        == value
    )


def test_value_to_bool(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    assert (
        builder.add(predicate, True)
        .build()
        .value(predicate)
        .unwrap()
        .to_bool()
        .unwrap()
        is True
    )


def test_value_to_bytes(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = b"test"
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_bytes()
        .unwrap()
        == value
    )


def test_value_to_collection(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    assert (
        builder.add(predicate, RDF.nil)
        .build()
        .value(predicate)
        .unwrap()
        .to_collection()
        .unwrap()
        == ()
    )


def test_value_to_date(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = date(2025, 3, 22)
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_date()
        .unwrap()
        == value
    )


def test_value_to_date_or_datetime(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = date(2025, 3, 22)
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_date_or_date_time()
        .unwrap()
        == value
    )


def test_value_to_datetime(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = datetime(2025, 3, 22, 5, 6, 7)
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_date()
        .unwrap()
        == value
    )


def test_value_to_decimal(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    assert builder.add(predicate, 1).build().value(
        predicate
    ).unwrap().to_decimal().unwrap() == Decimal(1)


def test_value_to_float(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    assert (
        builder.add(predicate, 1.2)
        .build()
        .value(predicate)
        .unwrap()
        .to_float()
        .unwrap()
        == 1.2
    )


def test_value_to_identifier(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = rdf.BlankNode()
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_identifier()
        .unwrap()
        == value
    )


def test_value_to_int(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    assert (
        builder.add(predicate, Decimal(1.0))
        .build()
        .value(predicate)
        .unwrap()
        .to_int()
        .unwrap()
        == 1
    )


def test_value_to_iri(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = rdf.Iri("http://example.com/value")
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_iri()
        .unwrap()
        == value
    )


def test_value_to_named_resource(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = rdf.Iri("http://example.com/value")
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_named_resource()
        .unwrap()
        .iri
        == value
    )


def test_value_to_resource(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    value = rdf.Iri("http://example.com/value")
    assert (
        builder.add(predicate, value)
        .build()
        .value(predicate)
        .unwrap()
        .to_resource()
        .unwrap()
        .identifier
        == value
    )


def test_value_to_str(
    builder: rdf.Resource.Builder, predicate: rdf.Quad_Predicate
) -> None:
    assert (
        builder.add(predicate, "test")
        .build()
        .value(predicate)
        .unwrap()
        .to_str()
        .unwrap()
        == "test"
    )
