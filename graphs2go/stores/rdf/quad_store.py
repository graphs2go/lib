from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pathvalidate import sanitize_filename
from returns.pipeline import is_successful

from graphs2go.models import rdf
from graphs2go.stores.store import Store

if TYPE_CHECKING:
    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class QuadStore(rdf.Dataset, Store):
    """
    An RDF quad store / persistent RDF Dataset.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

        identifier: Store.Identifier

    def __init__(self, *, identifier: Store.Identifier):
        self.__identifier = identifier

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @staticmethod
    def create(*, config: RdfStoreConfig, identifier: Store.Identifier) -> QuadStore:
        config_parsed = config.parse()

        from .oxigraph_quad_store import OxigraphQuadStore

        if not is_successful(config_parsed.oxigraph_directory_path):
            raise NotImplementedError

        oxigraph_directory_path = (
            config_parsed.oxigraph_directory_path.unwrap()
            / sanitize_filename(identifier.namespace)
            / sanitize_filename(identifier.name)
        )
        oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphQuadStore(
            directory_path=oxigraph_directory_path,
            identifier=identifier,
            read_only=False,
            transactional=config_parsed.transactional,
        )

    @property
    @abstractmethod
    def descriptor(self) -> Descriptor:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    @property
    def identifier(self) -> Store.Identifier:
        return self.__identifier

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> QuadStore:
        from .oxigraph_quad_store import OxigraphQuadStore

        if isinstance(descriptor, OxigraphQuadStore.Descriptor):
            return OxigraphQuadStore.open(descriptor, read_only=read_only)

        raise TypeError(type(descriptor))
