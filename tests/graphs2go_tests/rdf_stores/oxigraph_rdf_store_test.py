from collections.abc import Iterable
from pathlib import Path

import pytest

from graphs2go.rdf_stores.oxigraph_rdf_store import OxigraphRdfStore
from graphs2go.rdf_stores.rdf_store import RdfStore
from tests.graphs2go_tests.rdf_stores.rdf_store_test import RdfStoreTest


class TestOxigraphRdfStore(RdfStoreTest):
    @pytest.fixture()
    def rdf_store(self, tmp_path: Path) -> Iterable[RdfStore]:
        with OxigraphRdfStore(
            oxigraph_directory_path=tmp_path, read_only=False, transactional=True
        ) as rdf_store:
            yield rdf_store
