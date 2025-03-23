from __future__ import annotations

import base64
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Self, cast

from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from graphs2go.models.rdf.blank_node import BlankNode
from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.literal import Literal
from graphs2go.models.rdf.quad import Quad, Quad_Object, Quad_Predicate
from graphs2go.namespaces import RDF, XSD

if TYPE_CHECKING:
    from collections.abc import Iterable

    from graphs2go.models.rdf import NamedResource
    from graphs2go.models.rdf.dataset import Dataset


class Resource:
    """
    Bespoke RDF Resource class, in lieu of the rdflib Resource.
    """

    Identifier = BlankNode | Iri

    class Builder:
        _AddableValue = Quad_Object | bool | bytes | date | datetime | float | int | str

        def __init__(
            self, *, dataset: Dataset, identifier: Resource.Identifier
        ) -> None:
            self.__dataset = dataset
            self.__identifier = identifier

        def add(self, predicate: Quad_Predicate, value: _AddableValue) -> Self:
            self.__dataset.add(
                Quad(self.__identifier, predicate, self.__value_to_quad_object(value))
            )
            return self

        def build(self) -> Resource:
            return Resource(dataset=self.__dataset, identifier=self.__identifier)

        @property
        def dataset(self) -> Dataset:
            return self.__dataset

        @property
        def identifier(self) -> Resource.Identifier:
            return self.__identifier

        def set(self, predicate: Quad_Predicate, value: _AddableValue) -> Self:
            self.__dataset.remove_matches(self.__identifier, predicate)
            self.__dataset.add(
                Quad(self.__identifier, predicate, self.__value_to_quad_object(value))
            )
            return self

        @staticmethod
        def __value_to_quad_object(value: _AddableValue) -> Quad_Object:
            if isinstance(value, BlankNode):
                return value
            if isinstance(value, bytes):
                return Literal(base64.encodebytes(value), datatype=XSD.base64Binary)
            if isinstance(value, date):
                return Literal(value)
            if isinstance(value, datetime):
                return Literal(value)
            if isinstance(value, Decimal):
                return Literal(value)
            if isinstance(value, float):
                return Literal(value)
            if isinstance(value, int):
                return Literal(value)
            if isinstance(value, Iri):
                return value
            if isinstance(value, Literal):
                return value
            if isinstance(value, str):
                return Literal(value)
            raise TypeError(type(value))

    class Value:
        def __init__(
            self, *, object_: Quad_Object, predicate: Quad_Predicate, subject: Resource
        ):
            self.__object = object_
            self.__predicate = predicate
            self.__subject = subject

        def __cast[T](
            self,
            value: Any,  # noqa: ANN401
            types: type[T] | tuple[type[T], ...],
        ) -> Result[T, ValueError]:
            if isinstance(value, types):
                return Success(value)
            return Failure(
                ValueError(
                    f"{self.__subject.identifier} {self.__predicate} is not a {types} but a {type(value)}"
                )
            )

        def to_blank_node(self) -> Result[BlankNode, ValueError]:
            return self.__cast(self.__object, BlankNode)

        def to_bool(self) -> Result[bool, ValueError]:
            return self.__to_python().bind(lambda py: self.__cast(py, bool))

        def to_bytes(self) -> Result[bytes, ValueError]:
            return self.__to_python().bind(lambda py: self.__cast(py, bytes))

        def to_collection(self) -> Result[tuple[Resource.Value, ...], ValueError]:
            def __to_collection(
                resource: Resource,
            ) -> Result[tuple[Resource.Value, ...], ValueError]:
                if resource.identifier == RDF.nil:
                    return Success(())
                first = resource.value(RDF.first)
                if not is_successful(first):
                    return Failure(
                        ValueError(f"{resource.identifier} has no rdf:first")
                    )
                rest = resource.value(RDF.rest)
                if not is_successful(rest):
                    return Failure(ValueError(f"{resource.identifier} has no rdf:rest"))
                rest_collection = rest.unwrap().to_collection()
                if not is_successful(rest_collection):
                    return rest_collection
                return Success((first.unwrap(), *rest_collection.unwrap()))

            return self.to_resource().bind(__to_collection)

        def to_date(self) -> Result[date, ValueError]:
            return self.__to_python().bind(lambda py: self.__cast(py, date))

        def to_date_or_date_time(self) -> Result[date | datetime, ValueError]:
            return self.__to_python().bind(lambda py: self.__cast(py, (date, datetime)))

        def to_datetime(self) -> Result[datetime, ValueError]:
            return self.__to_python().bind(lambda py: self.__cast(py, datetime))

        def to_decimal(self) -> Result[Decimal, ValueError]:
            return (
                self.__to_python()
                .bind(lambda py: self.__cast(py, (Decimal, float, int, str)))
                .map(
                    lambda number: Decimal(cast("Decimal | float | int | str", number))
                )
            )

        def to_float(self) -> Result[float, ValueError]:
            return (
                self.__to_python()
                .bind(lambda py: self.__cast(py, (Decimal, float, int, str)))
                .map(lambda number: float(cast("Decimal | float | int | str", number)))
            )

        def to_identifier(self) -> Result[Resource.Identifier, ValueError]:
            return self.__cast(self.__object, (BlankNode, Iri))

        def to_int(self) -> Result[int, ValueError]:
            return (
                self.__to_python()
                .bind(lambda py: self.__cast(py, (Decimal, float, int, str)))
                .map(lambda number: int(cast("Decimal | float | int | str", number)))
            )

        def to_iri(self) -> Result[Iri, ValueError]:
            return self.__cast(self.__object, Iri)

        def to_literal(self) -> Result[Literal, ValueError]:
            return self.__cast(self.__object, Literal)

        def to_named_resource(self) -> Result[NamedResource, ValueError]:
            from graphs2go.models.rdf.named_resource import NamedResource

            return self.to_iri().map(
                lambda iri: NamedResource(dataset=self.__subject.dataset, iri=iri)
            )

        def __to_python(
            self,
        ) -> Result[
            bool | bytes | date | datetime | Decimal | float | int | str, ValueError
        ]:
            return self.to_literal().map(lambda literal: literal.toPython())

        def to_resource(self) -> Result[Resource, ValueError]:
            return self.to_identifier().map(
                lambda identifier: Resource(
                    dataset=self.__subject.dataset, identifier=identifier
                )
            )

        def to_str(self) -> Result[str, ValueError]:
            return self.__to_python().bind(lambda py: self.__cast(py, str))

        def to_term(self) -> Quad_Object:
            return self.__object

    def __init__(self, *, dataset: Dataset, identifier: BlankNode | Iri):
        self.__dataset = dataset
        self.__identifier = identifier

    @classmethod
    def builder(
        cls, *, identifier: Identifier, dataset: Maybe[Dataset] = Nothing
    ) -> Builder:
        if is_successful(dataset):
            return cls.Builder(dataset=dataset.unwrap(), identifier=identifier)

        from graphs2go.models.rdf.oxigraph_dataset import OxigraphDataset

        return cls.Builder(dataset=OxigraphDataset(), identifier=identifier)

    @property
    def dataset(self) -> Dataset:
        return self.__dataset

    @property
    def identifier(self) -> Identifier:
        return self.__identifier

    def value(self, predicate: Iri) -> Maybe[Value]:
        for value in self.values(predicate):
            return Some(value)
        return Nothing

    def values(self, predicate: Iri) -> Iterable[Value]:
        for quad in self.__dataset.match(self.__identifier, predicate):
            yield self.Value(object_=quad.object_, predicate=predicate, subject=self)
