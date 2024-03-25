from typing import TYPE_CHECKING

from graphs2go.models import interchange, cypher
from graphs2go.transformers.transform_interchange_graph_to_cypher_statements import (
    transform_interchange_graph_to_cypher_statements,
)


def test_transform(interchange_graph: interchange.Graph) -> None:
    cypher_statements = tuple(
        transform_interchange_graph_to_cypher_statements(interchange_graph)
    )

    assert len(
        tuple(s for s in cypher_statements if isinstance(s, cypher.CreateNodeStatement))
    ) == len(tuple(interchange_graph.nodes()))

    # assert len(
    #     tuple(
    #         s
    #         for s in cypher_statements
    #         if isinstance(s, cypher.CreateRelationshipStatement)
    #     )
    # ) == sum(
    #     len(tuple(interchange_node.relationships))
    #     for interchange_node in interchange_graph.nodes()
    # )
