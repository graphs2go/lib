from collections.abc import Iterable
from pathlib import Path
import pytest
import rdflib.store

from graphs2go.rdf_stores.rdf_store import RdfStore


class RdfStoreTest:
    @pytest.fixture()
    def rdf_store(self, tmp_path: Path) -> Iterable[RdfStore]:  # noqa: PT004
        raise NotImplementedError

    def test_bulk_load(self, rdf_store: RdfStore) -> None:
        assert rdf_store.is_empty
        rdf_store.bulk_load(
            mime_type="text/turtle", source=Path(__file__).parent / "example.ttl"
        )
        assert not rdf_store.is_empty

    def test_is_empty(self, rdf_store: RdfStore) -> None:
        assert rdf_store.is_empty

    def __test_open(self, *, rdf_store: RdfStore, read_only: bool) -> None:
        assert rdf_store.is_empty
        rdf_store.bulk_load(
            mime_type="text/turtle", source=Path(__file__).parent / "example.ttl"
        )
        assert not rdf_store.is_empty

        descriptor = rdf_store.descriptor
        assert isinstance(descriptor, RdfStore.Descriptor)
        rdf_store.close()

        with rdf_store.__class__.open(
            descriptor, read_only=read_only
        ) as open_rdf_store:
            assert not open_rdf_store.is_empty

    def test_open_read_only(self, rdf_store: RdfStore) -> None:
        self.__test_open(rdf_store=rdf_store, read_only=True)

    def test_open_read_write(self, rdf_store: RdfStore) -> None:
        self.__test_open(rdf_store=rdf_store, read_only=False)

    def test_rdflib_store(self, rdf_store: RdfStore) -> None:
        assert isinstance(rdf_store.rdflib_store, rdflib.store.Store)
