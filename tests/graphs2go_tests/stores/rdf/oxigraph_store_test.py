from collections.abc import Iterable
from pathlib import Path

import pytest
from returns.maybe import Some

from graphs2go.stores.rdf import Store
from graphs2go.stores.rdf.oxigraph_store import OxigraphStore
from tests.graphs2go_tests.stores.rdf.store_test import StoreTest


class TestOxigraphStore(StoreTest):
    @pytest.fixture()
    def store(self, tmp_path: Path) -> Iterable[Store]:
        with OxigraphStore(
            directory_path=Some(tmp_path), read_only=False, transactional=True
        ) as rdf_store:
            yield rdf_store
