from collections.abc import Iterable
from pathlib import Path

import pytest

from graphs2go.models import rdf
from graphs2go.stores.rdf import QuadStore


class QuadStoreTest:
    class _TestData:
        BLANK_NODE_SUBJECT = rdf.BlankNode()
        IRI_SUBJECT = rdf.Iri("http://example.com/subject")
        BLANK_NODE_OBJECT = rdf.BlankNode()
        IRI_OBJECT = rdf.Iri("http://example.com/object")
        LITERAL_OBJECT = rdf.Literal("object")
        PREDICATE = rdf.Iri("http://example.com/predicate")
        QUAD = rdf.Quad(
            IRI_SUBJECT,
            PREDICATE,
            IRI_OBJECT,
        )
        TTL_FILE_PATH = Path(__file__).parent / "example.ttl"

    @pytest.fixture()
    def quad_store(self, tmp_path: Path) -> Iterable[QuadStore]:
        raise NotImplementedError

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_add(self, quad_store: QuadStore) -> None:  # noqa: N802
        assert quad_store.is_empty
        quad_store.add(self._TestData.QUAD)
        assert not quad_store.is_empty

    def test_extend(self, quad_store: QuadStore) -> None:  # noqa: N802
        quad_store.extend(
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
        assert len(quad_store) == 3

    def test_clear(self, quad_store: QuadStore) -> None:
        assert quad_store.is_empty
        quad_store.add(self._TestData.QUAD)
        assert not quad_store.is_empty
        quad_store.clear()
        assert quad_store.is_empty

    def test_close(self, quad_store: QuadStore) -> None:
        quad_store.close()

    def test_descriptor(self, quad_store: QuadStore) -> None:
        assert isinstance(quad_store.descriptor, QuadStore.Descriptor)

    def test_dump_prefixes(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        output = quad_store.dump(
            format_=rdf.Format.TURTLE, prefixes={"ex": rdf.Iri("http://example.com/")}
        ).decode("utf-8")
        assert (
            output
            == "@prefix ex: <http://example.com/> .\nex:subject ex:predicate ex:object .\n"
        )

    def test_dump_to_bytes(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        output = quad_store.dump(format_=rdf.Format.NQUADS).decode("utf-8")
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
    def test_is_empty(self, quad_store: QuadStore) -> None:
        assert quad_store.is_empty

    def test_len(self, quad_store: QuadStore) -> None:
        assert len(quad_store) == 0
        quad_store.add(self._TestData.QUAD)
        assert len(quad_store) == 1
        quad_store.add(self._TestData.QUAD)
        assert len(quad_store) == 1

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_load_from_file(self, quad_store: QuadStore) -> None:
        assert quad_store.is_empty
        quad_store.load(
            format_=rdf.Format.TURTLE, input_=Path(__file__).parent / "example.ttl"
        )
        assert not quad_store.is_empty

    def test_match_empty(self, quad_store: QuadStore) -> None:
        assert len(tuple(quad_store.match())) == 0

    def test_match_exact(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        matches = tuple(quad_store.match(*self._TestData.QUAD))
        assert len(matches) == 1
        assert matches[0] == self._TestData.QUAD

    def test_match_mismatch(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        assert (
            len(
                tuple(
                    quad_store.match(
                        self._TestData.QUAD.subject,
                        self._TestData.QUAD.predicate,
                        self._TestData.BLANK_NODE_OBJECT,
                    )
                )
            )
            == 0
        )

    def test_match_wildcard(self, quad_store: QuadStore) -> None:
        quad_store.add(self._TestData.QUAD)
        matches = tuple(
            quad_store.match(self._TestData.QUAD.subject, self._TestData.QUAD.predicate)
        )
        assert len(matches) == 1
        assert matches[0] == self._TestData.QUAD

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
        self.__test_open(store=quad_store, read_only=True)

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_open_read_write(self, quad_store: QuadStore) -> None:
        self.__test_open(store=quad_store, read_only=False)

    def test_remove(self, quad_store: QuadStore) -> None:
        quad_store.remove(self._TestData.QUAD)
        quad_store.add(self._TestData.QUAD)
        assert not quad_store.is_empty
        quad_store.remove(
            rdf.Quad(
                self._TestData.QUAD.subject,
                self._TestData.QUAD.predicate,
                self._TestData.BLANK_NODE_OBJECT,
            )
        )
        assert not quad_store.is_empty
        quad_store.remove(self._TestData.QUAD)
        assert quad_store.is_empty
