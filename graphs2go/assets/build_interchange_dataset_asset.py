from collections.abc import Iterable

from dagster import AssetsDefinition, asset, get_dagster_logger
from rdflib import BNode, ConjunctiveGraph, URIRef
from graphs2go.loaders.rdf_directory_loader import RdfDirectoryLoader
from graphs2go.models.interchange.dataset import Dataset
from graphs2go.models.interchange.model import Model
from graphs2go.resources.interchange_config import InterchangeConfig


def build_interchange_dataset_asset(
    *, interchange_dataset_identifier: URIRef, interchange_models: Iterable[Model]
) -> AssetsDefinition:
    @asset(code_version="1")
    def interchange_dataset(interchange_config: InterchangeConfig) -> Dataset:
        interchange_config_parsed = interchange_config.parse()
        loader = RdfDirectoryLoader.create(
            directory_path=interchange_config_parsed.directory_path,
            rdf_format=interchange_config_parsed.rdf_format,
        )
        dataset_file_path = loader.rdf_graph_file_path(interchange_dataset_identifier)
        logger = get_dagster_logger()

        if dataset_file_path.is_file():
            if interchange_config_parsed.recreate:
                logger.info(
                    "interchange dataset %s already exists but recreate specified, deleting",
                    dataset_file_path,
                )
                dataset_file_path.unlink()
            else:
                logger.info(
                    "interchange dataset %s already exists, skipping build",
                    dataset_file_path,
                )
                return Dataset(identifier=interchange_dataset_identifier)

        for interchange_model in interchange_models:
            # Always load conjunctive graph with the dataset identifier so that everything ends up in the same place
            conjunctive_graph = ConjunctiveGraph(
                identifier=interchange_dataset_identifier
            )

            # Copy the model graph to the conjunctive graph
            if isinstance(interchange_model.resource.graph.identifier, BNode):
                # No explicit graph identifier = dump the triples into the conjunctive graph's default graph
                graph = conjunctive_graph.default_context
            else:
                # Else put the triples into the right named graph on the conjunctive graph
                # A model can't be spread across multiple named graphs
                graph = conjunctive_graph.get_context(
                    interchange_model.resource.graph.identifier
                )
            graph += interchange_model.resource.graph

            loader(graph)

        return Dataset(identifier=interchange_dataset_identifier)

    return interchange_dataset
