from collections.abc import Iterable
from pathlib import Path

import pytest

from graphs2go.models import rdf
from graphs2go.stores.rdf import Store


class StoreTest:
    class _TestData:
        BLANK_NODE_SUBJECT = rdf.BlankNode()
        IRI_SUBJECT = rdf.Iri("http://example.org/subject")
        BLANK_NODE_OBJECT = rdf.BlankNode()
        IRI_OBJECT = rdf.Iri("http://example.org/object")
        LITERAL_OBJECT = rdf.Literal("object")
        PREDICATE = rdf.Iri("http://example.org/predicate")
        QUAD = rdf.Quad(
            IRI_SUBJECT,
            PREDICATE,
            IRI_OBJECT,
        )
        TTL_FILE_PATH = Path(__file__).parent / "example.ttl"

    @pytest.fixture()
    def store(self, tmp_path: Path) -> Iterable[Store]:
        raise NotImplementedError

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_add(self, store: Store) -> None:  # noqa: N802
        assert store.is_empty
        store.add(self._TestData.QUAD)
        assert not store.is_empty

    def test_extend(self, store: Store) -> None:  # noqa: N802
        store.extend(
            (
                rdf.Quad(
                    self._TestData.IRI_SUBJECT,
                    self._TestData.PREDICATE,
                    self._TestData.IRI_OBJECT,
                ),
                rdf.Quad(
                    self._TestData.BLANK_NODE_SUBJECT,
                    self._TestData.PREDICATE,
                    self._TestData.BLANK_NODE_OBJECT,
                ),
                rdf.Quad(
                    self._TestData.IRI_SUBJECT,
                    self._TestData.PREDICATE,
                    self._TestData.LITERAL_OBJECT,
                ),
            )
        )
        assert len(store) == 3

    def test_close(self, store: Store) -> None:
        store.close()

    def test_descriptor(self, store: Store) -> None:
        assert isinstance(store.descriptor, Store.Descriptor)

    def test_dump_to_bytes(self, store: Store) -> None:
        store.add(self._TestData.QUAD)
        output = store.dump(format_=rdf.Format.NQUADS).decode("utf-8")
        assert (
            output
            == "<http://example.org/subject> <http://example.org/predicate> <http://example.org/object> .\n"
        )

    def test_dump_to_file(self, store: Store, tmp_path: Path) -> None:
        store.add(self._TestData.QUAD)
        output_file_path = tmp_path / "temp.nq"
        output = store.dump(format_=rdf.Format.NQUADS, output=output_file_path)
        assert output is None
        assert output_file_path.is_file()
        with output_file_path.open() as output_file:
            assert (
                output_file.read()
                == "<http://example.org/subject> <http://example.org/predicate> <http://example.org/object> .\n"
            )

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_is_empty(self, store: Store) -> None:
        assert store.is_empty

    def test_len(self, store: Store) -> None:
        assert len(store) == 0
        store.add(self._TestData.QUAD)
        assert len(store) == 1
        store.add(self._TestData.QUAD)
        assert len(store) == 1

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_load_from_file(self, store: Store) -> None:
        assert store.is_empty
        store.load(
            format_=rdf.Format.TURTLE, input_=Path(__file__).parent / "example.ttl"
        )
        assert not store.is_empty

    def test_match_empty(self, store: Store) -> None:
        assert len(tuple(store.match())) == 0

    def test_match_exact(self, store: Store) -> None:
        store.add(self._TestData.QUAD)
        matches = tuple(store.match(*self._TestData.QUAD))
        assert len(matches) == 1
        assert matches[0] == self._TestData.QUAD

    def test_match_mismatch(self, store: Store) -> None:
        store.add(self._TestData.QUAD)
        assert (
            len(
                tuple(
                    store.match(
                        self._TestData.QUAD.subject,
                        self._TestData.QUAD.predicate,
                        self._TestData.BLANK_NODE_OBJECT,
                    )
                )
            )
            == 0
        )

    def test_match_wildcard(self, store: Store) -> None:
        store.add(self._TestData.QUAD)
        matches = tuple(
            store.match(self._TestData.QUAD.subject, self._TestData.QUAD.predicate)
        )
        assert len(matches) == 1
        assert matches[0] == self._TestData.QUAD

    def __test_open(self, *, store: Store, read_only: bool) -> None:
        assert store.is_empty
        store.load(format_=rdf.Format.TURTLE, input_=self._TestData.TTL_FILE_PATH)
        assert not store.is_empty

        descriptor = store.descriptor
        assert isinstance(descriptor, Store.Descriptor)
        store.close()

        with store.__class__.open(descriptor, read_only=read_only) as open_store:
            assert not open_store.is_empty

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_only(self, store: Store) -> None:
        self.__test_open(store=store, read_only=True)

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_write(self, store: Store) -> None:
        self.__test_open(store=store, read_only=False)
