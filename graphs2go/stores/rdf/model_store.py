from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, TypeVar

from returns.maybe import Maybe, Nothing

from graphs2go.models import rdf
from graphs2go.stores.rdf import QuadStore

if TYPE_CHECKING:

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


ModelT = TypeVar("ModelT", bound=rdf.Model)


class ModelStore[ModelT](rdf.ModelSet[ModelT]):
    """
    Non-picklable RDF model store backed by an RDF quad store.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF model store.
        """

        identifier: rdf.Iri
        quad_store_descriptor: QuadStore.Descriptor

    def __init__(self, *, identifier: rdf.Iri, quad_store: QuadStore):
        rdf.ModelSet.__init__(self, dataset=quad_store)
        self.__identifier = identifier
        self.__quad_store = quad_store

    def close(self) -> None:
        self.__quad_store.close()

    @classmethod
    def create(
        cls, *, identifier: rdf.Iri, quad_store_config: Maybe[RdfStoreConfig] = Nothing
    ) -> Self:
        return cls(
            identifier=identifier,
            quad_store=QuadStore.create(
                config=quad_store_config, identifier=identifier
            ),
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            identifier=self.__identifier,
            quad_store_descriptor=self.__quad_store.descriptor,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @property
    def identifier(self) -> rdf.Iri:
        return self.__identifier

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> Self:
        return cls(
            identifier=descriptor.identifier,
            quad_store=QuadStore.open(
                descriptor.quad_store_descriptor, read_only=read_only
            ),
        )
