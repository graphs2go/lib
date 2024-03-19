from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import oxrdflib
import pyoxigraph
from pathvalidate import sanitize_filename

from graphs2go.rdf_stores.rdf_store import RdfStore

if TYPE_CHECKING:
    from pathlib import Path

    import rdflib.store
    from rdflib import URIRef

    from graphs2go.resources.rdf_store_config import RdfStoreConfig


class OxigraphRdfStore(RdfStore):
    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        oxigraph_directory_path: Path

    def __init__(
        self,
        *,
        oxigraph_directory_path: Path,
    ):
        self.__oxigraph_directory_path = oxigraph_directory_path
        self.__pyoxigraph_store = pyoxigraph.Store(oxigraph_directory_path)
        self.__rdflib_store = oxrdflib.OxigraphStore(store=self.__pyoxigraph_store)

    def bulk_load(self, *, mime_type: str, source: Path) -> None:
        self.pyoxigraph_store.bulk_load(input=source, mime_type=mime_type)

    def close(self) -> None:
        del self.__pyoxigraph_store

    @staticmethod
    def create(
        *,
        identifier: URIRef,
        rdf_store_config_parsed: RdfStoreConfig.Parsed,
    ) -> OxigraphRdfStore:
        oxigraph_directory_path = (
            rdf_store_config_parsed.directory_path / sanitize_filename(identifier)
        )
        oxigraph_directory_path.mkdir(parents=True, exist_ok=True)
        return OxigraphRdfStore(
            oxigraph_directory_path=oxigraph_directory_path,
        )

    @property
    def descriptor(self) -> Descriptor:
        return self.Descriptor(
            oxigraph_directory_path=self.__oxigraph_directory_path,
        )

    @staticmethod
    def open(descriptor: Descriptor) -> OxigraphRdfStore:
        return OxigraphRdfStore(
            oxigraph_directory_path=descriptor.oxigraph_directory_path,
        )

    @property
    def rdflib_store(self) -> rdflib.store.Store:
        return self.__rdflib_store

    @property
    def pyoxigraph_store(self) -> pyoxigraph.Store:
        return self.__pyoxigraph_store
