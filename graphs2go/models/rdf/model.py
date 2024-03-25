from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import TYPE_CHECKING, Self, TypeVar

import rdflib.collection
from rdflib import RDF, Graph, Literal, URIRef
from rdflib.resource import Resource

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable

    from rdflib.term import Node


_ModelT = TypeVar("_ModelT", bound="Model")
_StatementObject = Literal | Resource
_ValueT = TypeVar("_ValueT")

logger = logging.getLogger(__name__)


class Model(ABC):
    """
    Abstract base class for models backed by an rdflib Resource.
    """

    class Builder(ABC):
        def __init__(self, resource: Resource):
            if not isinstance(resource.identifier, URIRef):
                raise TypeError("expected URI-identified resource")
            self.__resource = resource

        def _add(
            self, predicate: URIRef, object_: Literal | Model | URIRef | None
        ) -> Self:
            if object_ is not None:
                if isinstance(object_, Model):
                    self._resource.add(predicate, object_.uri)
                else:
                    self._resource.add(predicate, object_)
            return self

        def _set(
            self, predicate: URIRef, object_: Literal | Model | URIRef | None
        ) -> Self:
            if object_ is not None:
                if isinstance(object_, Model):
                    self._resource.set(predicate, object_.uri)
                else:
                    self._resource.set(predicate, object_)
            else:
                self._resource.remove(predicate)
            return self

        @abstractmethod
        def build(self) -> Model:
            pass

        @property
        def _resource(self) -> Resource:
            return self.__resource

    def __init__(self, *, resource: Resource):
        if not isinstance(resource.identifier, URIRef):
            raise ValueError("model resource must be named")  # noqa: TRY004
        self.__resource = resource

    @classmethod
    def _create_resource(cls, uri: URIRef) -> Resource:
        resource = Graph().resource(uri)
        resource.add(RDF.type, cls.primary_rdf_type())
        return resource

    @staticmethod
    def _map_term_to_bool(term: _StatementObject) -> bool | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, bool):
                return py_value
        return None

    @staticmethod
    def _map_term_to_bytes(term: _StatementObject) -> bytes | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, bytes):
                return py_value
        return None

    @staticmethod
    def _map_term_to_float(term: _StatementObject) -> float | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, float):
                return py_value
            if isinstance(py_value, int):
                return float(py_value)
        return None

    @staticmethod
    def _map_term_to_int(term: _StatementObject) -> int | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, int):
                return py_value
        return None

    @staticmethod
    def _map_term_to_collection(
        term: _StatementObject,
    ) -> tuple[Node, ...] | None:
        if not isinstance(term, Resource):
            return None
        resource: Resource = term
        return tuple(rdflib.collection.Collection(resource.graph, resource.identifier))

    @staticmethod
    def _map_term_to_date_or_datetime(term: _StatementObject) -> date | datetime | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, date | datetime):
                return py_value
        return None

    @staticmethod
    def _map_term_to_datetime(term: _StatementObject) -> datetime | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, datetime):
                return py_value
        return None

    # @staticmethod
    # def _map_term_to_container(
    #     term: _StatementObject,
    # ) -> Optional[Tuple[BNode | Literal | URIRef]]:
    #     if not isinstance(term, Resource):
    #         return None
    #     resource: Resource = term
    #     result: List[BNode | Literal | URIRef] = []
    #     container_rdf_type = resource.value(RDF.type)
    #     container_class = rdflib.Container
    #     if isinstance(container_rdf_type, Resource):
    #         if container_rdf_type.identifier == RDF.Alt:
    #             container_class = rdflib.Alt
    #         elif container_rdf_type.identifier == RDF.Bag:
    #             container_class = rdflib.Bag
    #         elif container_rdf_type.identifier == RDF.Seq:
    #             container_class = rdflib.Seq
    #         elif container_rdf_type.identifier == RDF.List:
    #             container_class = rdflib.List
    #         else:
    #             raise NotImplementedError(container_rdf_type.identifier)
    #
    #     return tuple(container_class(resource.graph, resource.identifier))

    @staticmethod
    def _map_term_to_literal(term: _StatementObject) -> Literal | None:
        if isinstance(term, Literal):
            return term
        return None

    @staticmethod
    def _map_term_to_literal_or_uri(
        term: _StatementObject,
    ) -> Literal | URIRef | None:
        if isinstance(term, Literal):
            return term
        if isinstance(term, Resource) and isinstance(term.identifier, URIRef):
            return term.identifier
        return None

    @staticmethod
    def _map_term_to_model(
        model_class: type[_ModelT], term: _StatementObject
    ) -> _ModelT | None:
        model_or_uri = Model._map_term_to_model_or_uri(model_class, term)
        return model_or_uri if isinstance(model_or_uri, model_class) else None

    @staticmethod
    def _map_term_to_model_or_uri(
        model_class: type[_ModelT], term: _StatementObject
    ) -> _ModelT | URIRef | None:
        if not isinstance(term, Resource):
            return None
        resource: Resource = term
        if not isinstance(resource.identifier, URIRef):
            logger.warning("tried to map non-URI term to a model")
            return None

        value_type = resource.value(RDF.type)
        if not isinstance(value_type, Resource):
            if value_type is not None:
                logger.warning(
                    "term %s rdf:type is a %s, not a Resource",
                    term.identifier,
                    type(value_type),
                )
            return resource.identifier
        if value_type.identifier == model_class.primary_rdf_type():
            return model_class(resource=resource)

        return resource.identifier

    @staticmethod
    def _map_term_to_str(term: _StatementObject) -> str | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, str):
                return py_value
        return None

    @staticmethod
    def _map_term_to_str_or_uri(term: _StatementObject) -> str | URIRef | None:
        if isinstance(term, Literal):
            py_value = term.toPython()
            if isinstance(py_value, str):
                return py_value
        elif isinstance(term, Resource) and isinstance(term.identifier, URIRef):
            return term.identifier
        return None

    @staticmethod
    def _map_term_to_uri(term: _StatementObject) -> URIRef | None:
        if isinstance(term, Resource) and isinstance(term.identifier, URIRef):
            return term.identifier
        return None

    def _optional_value(
        self,
        predicate: URIRef,
        mapper: Callable[
            [_StatementObject], _ValueT | None
        ] = lambda value: value,  # type: ignore
    ) -> _ValueT | None:
        for value in self._values(predicate, mapper):
            return value
        return None

    @classmethod
    @abstractmethod
    def primary_rdf_type(cls) -> URIRef:
        pass

    def _required_value(
        self,
        predicate: URIRef,
        mapper: Callable[[_StatementObject], _ValueT | None] = lambda value: value,  # type: ignore
    ) -> _ValueT:
        for value in self._values(predicate, mapper):
            return value
        raise KeyError(f"{self.uri} missing required {predicate}")

    @property
    def rdf_types(self) -> Iterable[URIRef]:
        return self._values(RDF.type, self._map_term_to_uri)

    @property
    def resource(self) -> Resource:
        return self.__resource

    @property
    def secondary_rdf_types(self) -> Iterable[URIRef]:
        for rdf_type in self.rdf_types:
            if rdf_type != self.primary_rdf_type():
                yield rdf_type

    @property
    def uri(self) -> URIRef:
        return self.__resource.identifier

    def _values(
        self,
        predicate: URIRef,
        mapper: Callable[
            [_StatementObject], _ValueT | None
        ] = lambda value: value,  # type: ignore
    ) -> Generator[_ValueT, None, None]:
        for value in self.__resource.objects(predicate):
            mapped_value = mapper(value)
            if mapped_value is not None:
                yield mapped_value
