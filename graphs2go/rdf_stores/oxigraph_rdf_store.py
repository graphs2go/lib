from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import oxrdflib
import pyoxigraph
from pathvalidate import sanitize_filename

from graphs2go.rdf_stores.rdf_store import RdfStore

from oxrdflib import _to_ox

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from rdflib.graph import _QuadType
    import rdflib.store
    from rdflib import URIRef


class OxigraphRdfStore(RdfStore):
    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        oxigraph_directory_path: Path
        transactional: bool

    def __init__(
        self, *, oxigraph_directory_path: Path, read_only: bool, transactional: bool
    ):
        self.__oxigraph_directory_path = oxigraph_directory_path
        self.__pyoxigraph_store = (
            pyoxigraph.Store.secondary(str(oxigraph_directory_path))
            if read_only
            else pyoxigraph.Store(oxigraph_directory_path)
        )
        self.__rdflib_store = oxrdflib.OxigraphStore(store=self.__pyoxigraph_store)
        self.__transactional = transactional

    def add_all(self, quads: Iterable[_QuadType]) -> None:
        if self.__transactional:
            self.__pyoxigraph_store.extend(_to_ox(q) for q in quads)  # type: ignore
        else:
            self.__pyoxigraph_store.bulk_extend(_to_ox(q) for q in quads)  # type: ignore

    def load(self, *, mime_type: str, source: Path) -> None:
        if self.__transactional:
            self.pyoxigraph_store.load(input=source, mime_type=mime_type)
        else:
            self.pyoxigraph_store.bulk_load(input=source, mime_type=mime_type)

    def close(self) -> None:
        # There's no explicit close on the pyoxigraph Store.
        # Delete all references to the pyoxigraph Store so it gets garbage collected and releases its lock.
        try:
            del self.__pyoxigraph_store
            del self.__rdflib_store
        except AttributeError:
            pass

    @staticmethod
    def create(  # type: ignore
        *, identifier: URIRef, oxigraph_directory_path: Path, transactional: bool
    ) -> OxigraphRdfStore:
        oxigraph_subdirectory_path = oxigraph_directory_path / sanitize_filename(
            identifier
        )
        oxigraph_subdirectory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphRdfStore(
            oxigraph_directory_path=oxigraph_subdirectory_path,
            read_only=False,
            transactional=transactional,
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            oxigraph_directory_path=self.__oxigraph_directory_path,
            transactional=self.__transactional,
        )

    @staticmethod
    def open(  # type: ignore
        descriptor: RdfStore.Descriptor, *, read_only: bool = False
    ) -> OxigraphRdfStore:
        assert isinstance(descriptor, OxigraphRdfStore.Descriptor)
        return OxigraphRdfStore(
            oxigraph_directory_path=descriptor.oxigraph_directory_path,
            read_only=read_only,
            transactional=descriptor.transactional,
        )

    @property
    def rdflib_store(self) -> rdflib.store.Store:
        return self.__rdflib_store

    @property
    def pyoxigraph_store(self) -> pyoxigraph.Store:
        return self.__pyoxigraph_store
