from rdflib import ConjunctiveGraph, Graph
from loaders.rdf_graph_record import RdfGraphRecord
from loaders.rdf_loader import RdfLoader


class BufferingRdfLoader(RdfLoader):
    def __init__(self, *, default_rdf_graph_type: type[Graph] = Graph):
        self.__default_rdf_graph_type = default_rdf_graph_type
        self.__rdf_graphs_by_stream: dict[str, Graph] = {}

    def __call__(self, rdf_graph_record: RdfGraphRecord) -> None:
        stream_graph = self.__rdf_graphs_by_stream.get(rdf_graph_record.stream)
        if stream_graph is None:
            stream_graph = self.__rdf_graphs_by_stream[rdf_graph_record.stream] = (
                self.__default_rdf_graph_type()
            )

        if isinstance(rdf_graph_record.graph, ConjunctiveGraph) and isinstance(
            stream_graph, ConjunctiveGraph
        ):
            for quad in rdf_graph_record.graph.quads():
                stream_graph.add(quad)
        else:
            for triple in rdf_graph_record.graph:
                stream_graph.add(triple)

    def close(self) -> None:
        pass

    @property
    def rdf_graphs_by_stream(self) -> dict[str, Graph]:
        return self.__rdf_graphs_by_stream.copy()
