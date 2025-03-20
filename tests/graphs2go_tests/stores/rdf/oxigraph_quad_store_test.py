from collections.abc import Iterable
from pathlib import Path

import pytest
from returns.maybe import Some

from graphs2go.stores.rdf import QuadStore
from graphs2go.stores.rdf.oxigraph_quad_store import OxigraphQuadStore
from tests.graphs2go_tests.stores.rdf.quad_store_test import QuadStoreTest


class TestOxigraphQuadStoreTransactional(QuadStoreTest):
    @pytest.fixture()
    def quad_store(self, tmp_path: Path) -> Iterable[QuadStore]:
        with OxigraphQuadStore(
            directory_path=Some(tmp_path), read_only=False, transactional=True
        ) as store:
            yield store


class TestOxigraphQuadStoreNonTransactional(QuadStoreTest):
    @pytest.fixture()
    def quad_store(self, tmp_path: Path) -> Iterable[QuadStore]:
        with OxigraphQuadStore(
            directory_path=Some(tmp_path), read_only=False, transactional=False
        ) as store:
            yield store
