from collections.abc import Iterable
from pathlib import Path

import pytest

from graphs2go.models import rdf
from graphs2go.stores.rdf import QuadStore
from tests.graphs2go_tests.models.rdf.dataset_test import DatasetTest


class QuadStoreTest(DatasetTest):
    @pytest.fixture()
    def quad_store(self, tmp_path: Path) -> Iterable[QuadStore]:
        raise NotImplementedError

    def test_close(self, quad_store: QuadStore) -> None:
        quad_store.close()

    def test_descriptor(self, quad_store: QuadStore) -> None:
        assert isinstance(quad_store.descriptor, QuadStore.Descriptor)

    def __test_open(
        self, *, quad_store: QuadStore, read_only: bool, ttl_file_path: Path
    ) -> None:
        assert quad_store.is_empty
        quad_store.load(format_=rdf.Format.TURTLE, input_=ttl_file_path)
        assert not quad_store.is_empty

        descriptor = quad_store.descriptor
        assert isinstance(descriptor, QuadStore.Descriptor)
        quad_store.close()

        with quad_store.__class__.open(descriptor, read_only=read_only) as open_store:
            assert not open_store.is_empty

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_only(
        self, example_ttl_file_path: Path, quad_store: QuadStore
    ) -> None:
        self.__test_open(
            quad_store=quad_store, read_only=True, ttl_file_path=example_ttl_file_path
        )

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_write(
        self,
        quad_store: QuadStore,
        example_ttl_file_path: Path,
    ) -> None:
        self.__test_open(
            quad_store=quad_store, read_only=False, ttl_file_path=example_ttl_file_path
        )
