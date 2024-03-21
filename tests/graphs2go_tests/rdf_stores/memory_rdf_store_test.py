from collections.abc import Iterable
from pathlib import Path
import pytest
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.rdf_stores.rdf_store import RdfStore
from tests.graphs2go_tests.rdf_stores.rdf_store_test import RdfStoreTest


class TestMemoryRdfStore(RdfStoreTest):
    @pytest.fixture()
    def rdf_store(self, tmp_path: Path) -> Iterable[RdfStore]:  # noqa: ARG002
        yield MemoryRdfStore()  # noqa: PT022
