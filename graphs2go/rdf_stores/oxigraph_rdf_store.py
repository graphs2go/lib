from __future__ import annotations
from dataclasses import dataclass

from pathvalidate import sanitize_filename
from graphs2go.rdf_stores.rdf_store import RdfStore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rdflib.store import Store
    from graphs2go.resources.rdf_store_config import RdfStoreConfig
    from rdflib import URIRef
    from pathlib import Path


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

    @staticmethod
    def create(
        *,
        identifier: URIRef,
        rdf_store_config_parsed: RdfStoreConfig.Parsed,
    ) -> OxigraphRdfStore:
        oxigraph_directory_path = (
            rdf_store_config_parsed.directory_path
            / "interchange"
            / sanitize_filename(identifier)
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

    def to_rdflib_store(self) -> Store:
        import oxrdflib
        import pyoxigraph

        return oxrdflib.OxigraphStore(
            store=pyoxigraph.Store(self.__oxigraph_directory_path)
        )
