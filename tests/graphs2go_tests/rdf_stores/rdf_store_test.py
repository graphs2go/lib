from collections.abc import Iterable
from pathlib import Path

import pytest
from rdflib import Graph

from graphs2go.rdf_stores.rdf_store import RdfStore


class RdfStoreTest:
    @pytest.fixture()
    def rdf_store(self, tmp_path: Path) -> Iterable[RdfStore]:  # noqa: PT004
        raise NotImplementedError

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_addN(self, rdf_store: RdfStore) -> None:  # noqa: N802
        assert rdf_store.is_empty
        graph = Graph()
        graph.parse(source=Path(__file__).parent / "example.ttl")
        rdf_store.addN((s, p, o, graph) for s, p, o in graph)
        assert not rdf_store.is_empty

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_load(self, rdf_store: RdfStore) -> None:
        assert rdf_store.is_empty
        rdf_store.load(
            mime_type="text/turtle", source=Path(__file__).parent / "example.ttl"
        )
        assert not rdf_store.is_empty

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_is_empty(self, rdf_store: RdfStore) -> None:
        assert rdf_store.is_empty

    def __test_open(self, *, rdf_store: RdfStore, read_only: bool) -> None:
        assert rdf_store.is_empty
        rdf_store.load(
            mime_type="text/turtle", source=Path(__file__).parent / "example.ttl"
        )
        assert not rdf_store.is_empty

        descriptor = rdf_store.descriptor
        assert isinstance(descriptor, RdfStore.Descriptor)
        rdf_store.close()

        with rdf_store.__class__.open_(
            descriptor, read_only=read_only
        ) as open_rdf_store:
            assert not open_rdf_store.is_empty

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_only(self, rdf_store: RdfStore) -> None:
        self.__test_open(rdf_store=rdf_store, read_only=True)

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_write(self, rdf_store: RdfStore) -> None:
        self.__test_open(rdf_store=rdf_store, read_only=False)
