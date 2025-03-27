from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from typing import IO, TYPE_CHECKING

from pathvalidate import sanitize_filename
from returns.pipeline import is_successful

from graphs2go.models import rdf

if TYPE_CHECKING:
    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class QuadStore(rdf.Dataset):
    """
    An RDF quad store / persistent RDF Dataset.
    """

    @dataclass(frozen=True)
    class Descriptor:
        """
        A picklable dataclass identifying an RDF store. It can be used to open an RDF store.
        """

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @staticmethod
    def create(*, config: RdfStoreConfig, identifier: rdf.Iri) -> QuadStore:
        config_parsed = config.parse()

        from .oxigraph_quad_store import OxigraphQuadStore

        if not is_successful(config_parsed.oxigraph_directory_path):
            raise NotImplementedError

        oxigraph_directory_path = (
            config_parsed.oxigraph_directory_path.unwrap()
            / sanitize_filename(str(identifier))
        )
        oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphQuadStore(
            directory_path=oxigraph_directory_path,
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

    @classmethod
    def open(cls, descriptor: Descriptor, *, read_only: bool = False) -> QuadStore:
        from .oxigraph_quad_store import OxigraphQuadStore

        if isinstance(descriptor, OxigraphQuadStore.Descriptor):
            return OxigraphQuadStore.open(descriptor, read_only=read_only)

        raise TypeError(type(descriptor))
