from typing import override

from rdflib import ConjunctiveGraph, Graph, URIRef

from graphs2go.loaders.rdf_loader import RdfLoader


class BufferingRdfLoader(RdfLoader):
    def __init__(self, *, default_rdf_graph_type: type[Graph] = Graph):
        self.__default_rdf_graph_type = default_rdf_graph_type
        self.__rdf_graphs_by_identifier: dict[URIRef, Graph] = {}

    @override
    def load(self, rdf_graph: Graph) -> None:
        if not isinstance(rdf_graph.identifier, URIRef):
            raise ValueError("graph must have a named identifier")  # noqa: TRY004

        identifier_graph = self.__rdf_graphs_by_identifier.get(rdf_graph.identifier)
        if identifier_graph is None:
            identifier_graph = self.__rdf_graphs_by_identifier[rdf_graph.identifier] = (
                self.__default_rdf_graph_type(identifier=rdf_graph.identifier)
            )

        if isinstance(rdf_graph, ConjunctiveGraph) and isinstance(
            identifier_graph, ConjunctiveGraph
        ):
            for quad in rdf_graph.quads():
                identifier_graph.add(quad)
        else:
            for triple in rdf_graph:
                identifier_graph.add(triple)

        # Copy namespaces
        for prefix, namespace in rdf_graph.namespace_manager.namespaces():
            if prefix not in identifier_graph.namespace_manager:
                identifier_graph.bind(prefix, namespace)

    def close(self) -> None:
        pass

    @property
    def rdf_graphs_by_identifier(self) -> dict[URIRef, Graph]:
        return self.__rdf_graphs_by_identifier.copy()
