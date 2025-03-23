from collections.abc import Iterable
from pathlib import Path
from typing import cast

import pytest

from graphs2go.models import rdf
from graphs2go.stores.rdf import QuadStore
from tests.graphs2go_tests.models.rdf.dataset_test import DatasetTest


class QuadStoreTest(DatasetTest):
    class _TestData(DatasetTest._TestData):
        TTL_FILE_PATH = Path(__file__).parent / "example.ttl"

    def dataset(self, tmp_path: Path) -> Iterable[rdf.Dataset]:
        return self.quad_store(tmp_path)

    @pytest.fixture()
    def quad_store(self, tmp_path: Path) -> Iterable[QuadStore]:
        raise NotImplementedError

    def test_close(self, quad_store: QuadStore) -> None:
        quad_store.close()

    def test_descriptor(self, quad_store: QuadStore) -> None:
        assert isinstance(quad_store.descriptor, QuadStore.Descriptor)

    def test_dump_prefixes(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        output = cast(
            "bytes",
            quad_store.dump(
                format_=rdf.Format.TURTLE,
                prefixes={"ex": rdf.Iri("http://example.com/")},
            ),
        ).decode("utf-8")
        assert (
            output
            == "@prefix ex: <http://example.com/> .\nex:subject ex:predicate ex:object .\n"
        )

    def test_dump_to_bytes(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        output = cast("bytes", quad_store.dump(format_=rdf.Format.NQUADS)).decode(
            "utf-8"
        )
        assert (
            output
            == "<http://example.com/subject> <http://example.com/predicate> <http://example.com/object> .\n"
        )

    def test_dump_to_file(self, quad_store: QuadStore, tmp_path: Path) -> None:
        quad_store.add(self._TestData.QUAD)
        output_file_path = tmp_path / "temp.nq"
        output = quad_store.dump(format_=rdf.Format.NQUADS, output=output_file_path)
        assert output is None
        assert output_file_path.is_file()
        with output_file_path.open() as output_file:
            assert (
                output_file.read()
                == "<http://example.com/subject> <http://example.com/predicate> <http://example.com/object> .\n"
            )

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_load_from_file(self, quad_store: QuadStore) -> None:
        assert quad_store.is_empty
        quad_store.load(
            format_=rdf.Format.TURTLE, input_=Path(__file__).parent / "example.ttl"
        )
        assert not quad_store.is_empty

    def __test_open(self, *, quad_store: QuadStore, read_only: bool) -> None:
        assert quad_store.is_empty
        quad_store.load(format_=rdf.Format.TURTLE, input_=self._TestData.TTL_FILE_PATH)
        assert not quad_store.is_empty

        descriptor = quad_store.descriptor
        assert isinstance(descriptor, QuadStore.Descriptor)
        quad_store.close()

        with quad_store.__class__.open(descriptor, read_only=read_only) as open_store:
            assert not open_store.is_empty

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_only(self, quad_store: QuadStore) -> None:
        self.__test_open(quad_store=quad_store, read_only=True)

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_write(self, quad_store: QuadStore) -> None:
        self.__test_open(quad_store=quad_store, read_only=False)
