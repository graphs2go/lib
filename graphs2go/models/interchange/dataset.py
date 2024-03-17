from dataclasses import dataclass

import rdflib
from rdflib import URIRef

from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.resources.interchange_config import InterchangeConfig


@dataclass(frozen=True)
class Dataset:
    identifier: URIRef

    def to_rdflib_dataset(
        self, interchange_config: InterchangeConfig
    ) -> rdflib.Dataset:
        # TODO: check if Fuseki; if so, return an rdflib.Dataset backed by a SPARQLUpdateStore
        # Alternatively, use Oxigraph
        interchange_config_parsed = interchange_config.parse()

        rdf_file_path = RdfDirectoryLoader.create(
            directory_path=interchange_config_parsed.directory_path,
            rdf_format=interchange_config_parsed.rdf_format,
        ).rdf_graph_file_path(self.identifier)

        rdflib_dataset = rdflib.Dataset()
        rdflib_dataset.parse(rdf_file_path)

        return rdflib_dataset
