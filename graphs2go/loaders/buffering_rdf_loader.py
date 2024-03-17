from rdflib import ConjunctiveGraph, Graph

from graphs2go.loaders.rdf_loader import RdfLoader
from graphs2go.models.loadable_rdf_graph import LoadableRdfGraph


class BufferingRdfLoader(RdfLoader):
    def __init__(self, *, default_rdf_graph_type: type[Graph] = Graph):
        self.__default_rdf_graph_type = default_rdf_graph_type
        self.__rdf_graphs_by_stream: dict[str, Graph] = {}

    def __call__(self, loadable_rdf_graph: LoadableRdfGraph) -> None:
        stream_graph = self.__rdf_graphs_by_stream.get(loadable_rdf_graph.stream)
        if stream_graph is None:
            stream_graph = self.__rdf_graphs_by_stream[loadable_rdf_graph.stream] = (
                self.__default_rdf_graph_type()
            )

        if isinstance(loadable_rdf_graph.graph, ConjunctiveGraph) and isinstance(
            stream_graph, ConjunctiveGraph
        ):
            for quad in loadable_rdf_graph.graph.quads():
                stream_graph.add(quad)
        else:
            for triple in loadable_rdf_graph.graph:
                stream_graph.add(triple)

    def close(self) -> None:
        pass

    @property
    def rdf_graphs_by_stream(self) -> dict[str, Graph]:
        return self.__rdf_graphs_by_stream.copy()
