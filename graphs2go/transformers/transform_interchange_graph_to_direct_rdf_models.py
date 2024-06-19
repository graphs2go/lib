from collections.abc import Iterable

from graphs2go.models import interchange, rdf
from graphs2go.transformers.transform_interchange_graph import (
    transform_interchange_graph,
)


def _transform_interchange_node_to_direct_rdf_models(
    interchange_node: interchange.Node,  # noqa: ARG001
) -> Iterable[rdf.Model]:
    return ()


def transform_interchange_graph_to_direct_rdf_models(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
) -> Iterable[rdf.Model]:
    """
    Transform the interchange graph into a "direct" RDF representation, one with only as much reification as it
    needs to express the nodes, relationships, and properties in the interchange graph.

    "Direct" is used in the Wikidata sense of "direct claim".
    https://lists.wikimedia.org/hyperkitty/list/wikidata@lists.wikimedia.org/message/5YFA5QB7FCT2KIONGZX6GOTT4URHQRVJ/
    """

    yield from transform_interchange_graph(
        in_process=True,
        interchange_graph_descriptor=interchange_graph_descriptor,
        transform_interchange_node=_transform_interchange_node_to_direct_rdf_models,
    )
