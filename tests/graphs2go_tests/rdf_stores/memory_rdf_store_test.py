from collections.abc import Iterable
import pytest
from graphs2go.rdf_stores.memory_rdf_store import MemoryRdfStore
from graphs2go.rdf_stores.rdf_store import RdfStore
from tests.graphs2go_tests.rdf_stores.rdf_store_test import RdfStoreTest


class TestMemoryRdfStore(RdfStoreTest):
    @pytest.fixture()
    def rdf_store(self) -> Iterable[RdfStore]:
        yield MemoryRdfStore()  # noqa: PT022
