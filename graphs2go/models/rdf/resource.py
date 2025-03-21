from __future__ import annotations

from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Self

import rdflib.collection
from rdflib import Dataset
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import is_successful

from graphs2go.models.rdf.dataset import Dataset
from graphs2go.models.rdf.quad import Quad, Quad_Object, Quad_Predicate
from graphs2go.models.rdf.blank_node import BlankNode
from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.literal import Literal

if TYPE_CHECKING:
    from graphs2go.models.rdf.named_resource import NamedResource


class Resource:
    """
    Bespoke RDF Resource class, in lieu of the rdflib Resource.
    """

    Identifier = BlankNode | Iri

    class Builder:
        def __init__(
            self, *, dataset: Dataset, identifier: Resource.Identifier
        ) -> None:
            self.__identifier = identifier
            self.__dataset = dataset

        def add(self, predicate: Quad_Predicate, object_: Quad_Object) -> Self:
            self.__dataset.add(Quad(self.__identifier, predicate, object_))
            return self

        def build(self) -> Resource:
            return Resource(dataset=self.__dataset, identifier=self.__identifier)

        @property
        def identifier(self) -> Resource.Identifier:
            return self.__identifier

        def set(self, predicate: Quad_Predicate, object_: Quad_Object) -> Self:
            self.__dataset.remove_matches(self.__identifier, predicate)
            self.__dataset.add(Quad(self.__identifier, predicate, object_))
            return self

    # class ValueMappers:
    #     @staticmethod
    #     def bool(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[bool]:
    #         return Resource.ValueMappers.__py_value(object_, bool)
    #
    #     @staticmethod
    #     def bytes(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[bytes]:
    #         return Resource.ValueMappers.__py_value(object_, bytes)
    #
    #     @staticmethod
    #     def collection(
    #         _subject: Node, _predicate: Node, object_: Node, dataset: Dataset
    #     ) -> Maybe[tuple[Node, ...]]:
    #         if not isinstance(object_, BlankNode | Iri):
    #             return Nothing
    #         return Some(tuple(rdflib.collection.Collection(dataset, object_)))
    #
    #     @staticmethod
    #     def date_or_datetime(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[date | datetime]:
    #         if not isinstance(object_, Literal):
    #             return Nothing
    #         value_py = object_.toPython()
    #         if isinstance(value_py, date | datetime):
    #             return Some(value_py)
    #         return Nothing
    #
    #     @staticmethod
    #     def datetime(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[datetime]:
    #         return Resource.ValueMappers.__py_value(object_, datetime)
    #
    #     @staticmethod
    #     def float(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[float]:
    #         if not isinstance(object_, Literal):
    #             return Nothing
    #         value_py = object_.toPython()
    #         if isinstance(value_py, Decimal | float | int):
    #             return Some(float(value_py))
    #         return Nothing
    #
    #     @staticmethod
    #     def identifier(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[Resource.Identifier]:
    #         return Some(object_) if isinstance(object_, BlankNode | Iri) else Nothing
    #
    #     @staticmethod
    #     def identity(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[Node]:
    #         return Some(object_)
    #
    #     @staticmethod
    #     def int(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[int]:
    #         if not isinstance(object_, Literal):
    #             return Nothing
    #         value_py = object_.toPython()
    #         if isinstance(value_py, Decimal | float | int):
    #             return Some(int(value_py))
    #         return Nothing
    #
    #     @staticmethod
    #     def iri(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[Iri]:
    #         return Some(object_) if isinstance(object_, Iri) else Nothing
    #
    #     @staticmethod
    #     def literal(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[Literal]:
    #         return Some(object_) if isinstance(object_, Literal) else Nothing
    #
    #     @staticmethod
    #     def named_resource(
    #         subject: Node, predicate: Node, object_: Node, dataset: Dataset
    #     ) -> Maybe[NamedResource]:
    #         from .named_resource import NamedResource
    #
    #         return Resource.ValueMappers.iri(subject, predicate, object_, dataset).map(
    #             lambda iri: NamedResource(dataset=dataset, iri=iri)
    #         )
    #
    #     @staticmethod
    #     def __py_value(object_: Node, py_type: type[_PyValueT]) -> Maybe[_PyValueT]:
    #         if not isinstance(object_, Literal):
    #             return Nothing
    #         py_value = object_.toPython()
    #         return Some(py_value) if isinstance(py_value, py_type) else Nothing
    #
    #     @staticmethod
    #     def resource(
    #         subject: Node, predicate: Node, object_: Node, dataset: Dataset
    #     ) -> Maybe[Resource]:
    #         return Resource.ValueMappers.identifier(
    #             subject, predicate, object_, dataset
    #         ).map(lambda identifier: Resource(dataset=dataset, identifier=identifier))
    #
    #     @staticmethod
    #     def str(
    #         _subject: Node, _predicate: Node, object_: Node, _graph: Dataset
    #     ) -> Maybe[str]:
    #         return Resource.ValueMappers.__py_value(object_, str)

    def __init__(self, *, dataset: Dataset, identifier: BlankNode | Iri):
        self.__dataset = dataset
        self.__identifier = identifier

    @classmethod
    def builder(
        cls, *, identifier: Identifier, dataset: Maybe[Dataset] = Nothing
    ) -> Builder:
        return cls.Builder(
            dataset=dataset.or_else_call(lambda: Dataset()), identifier=identifier
        )

    @property
    def dataset(self) -> Dataset:
        return self.__dataset

    # def has_value(
    #     self, predicate: Iri, mapper: _ValueMapper = ValueMappers.identity
    # ) -> bool:
    #     for _value in self.values(predicate, mapper=mapper):  # type: ignore
    #         return True
    #     return False
    #
    # @property
    # def identifier(self) -> Identifier:
    #     return self.__identifier
    #
    # def optional_value(
    #     self, predicate: Iri, mapper: _ValueMapper = ValueMappers.identity
    # ) -> Maybe[_ValueT]:  # type: ignore
    #     for value in self.values(predicate, mapper=mapper):  # type: ignore
    #         return Some(value)
    #     return Nothing
    #
    # def optional_value_with_default(
    #     self,
    #     predicate: Iri,
    #     default: _ValueT,
    #     mapper: _ValueMapper = ValueMappers.identity,
    # ) -> _ValueT:  # type: ignore
    #     for value in self.values(predicate, mapper=mapper):  # type: ignore
    #         return value
    #     return default
    #
    # def required_value(
    #     self, predicate: Iri, mapper: _ValueMapper = ValueMappers.identity
    # ) -> _ValueT:  # type: ignore
    #     value: Maybe[_ValueT] = self.optional_value(predicate, mapper=mapper)
    #     if not is_successful(value):
    #         raise KeyError("missing required value for " + str(predicate))
    #     return value.unwrap()
    #
    # def values(
    #     self,
    #     predicate: Iri,
    #     mapper: _ValueMapper = ValueMappers.identity,
    #     unique: bool = False,
    # ) -> Iterable[_ValueT]:  # type: ignore
    #     for value in self.__dataset.objects(
    #         subject=self.identifier, predicate=predicate, unique=unique
    #     ):
    #         mapped_value = mapper(self.identifier, predicate, value, self.__dataset)
    #         if is_successful(mapped_value):
    #             yield mapped_value.unwrap()
