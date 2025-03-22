from graphs2go.models import cypher, interchange
from graphs2go.transformers.transform_interchange_models_to_cypher_statements import (
    transform_interchange_models_to_cypher_statements,
)


def test_transform(
    interchange_model_store_descriptor: InterchangeModelStore.Descriptor,
) -> None:
    cypher_statements = tuple(
        transform_interchange_models_to_cypher_statements(
            interchange_model_store_descriptor
        )
    )

    with InterchangeModelStore.open(
        interchange_model_store_descriptor, read_only=True
    ) as interchange_model_store:
        assert len(
            tuple(
                s
                for s in cypher_statements
                if isinstance(s, cypher.CreateNodeStatement)
            )
        ) == len(tuple(interchange_model_store.nodes()))

        assert len(
            tuple(
                s
                for s in cypher_statements
                if isinstance(s, cypher.CreateRelationshipStatement)
            )
        ) == sum(
            len(tuple(interchange_node.relationships()))
            for interchange_node in interchange_model_store.nodes()
        )
