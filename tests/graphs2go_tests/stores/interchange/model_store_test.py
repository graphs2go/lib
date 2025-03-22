from graphs2go.stores.interchange import ModelStore as InterchangeModelStore


def test_nodes(interchange_model_store: InterchangeModelStore) -> None:
    assert tuple(interchange_model_store.nodes())
