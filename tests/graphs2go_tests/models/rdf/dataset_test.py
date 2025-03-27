from collections.abc import Iterable
from pathlib import Path
from typing import cast

import pytest

from graphs2go.models import rdf


class DatasetTest:
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
    def dataset(self, tmp_path: Path) -> Iterable[rdf.Dataset]:
        raise NotImplementedError

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_add(self, dataset: rdf.Dataset) -> None:
        assert dataset.is_empty
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty

    def test_extend(self, dataset: rdf.Dataset) -> None:
        dataset.extend(
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
        assert len(dataset) == 3

    def test_clear(self, dataset: rdf.Dataset) -> None:
        assert dataset.is_empty
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.clear()
        assert dataset.is_empty

    def test_count_matches_all(self, dataset: rdf.Dataset) -> None:
        assert dataset.count_matches() == 0
        dataset.add(self._TestData.QUAD)
        assert dataset.count_matches() == 1

    def test_count_matches_exact(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert dataset.count_matches(*self._TestData.QUAD) == 1

    def test_count_matches_partial(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert (
            dataset.count_matches(
                self._TestData.QUAD.subject, self._TestData.QUAD.predicate
            )
            == 1
        )
        assert (
            dataset.count_matches(
                self._TestData.QUAD.subject,
                self._TestData.QUAD.predicate,
                self._TestData.BLANK_NODE_OBJECT,
            )
            == 0
        )

    def test_dump_prefixes(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        output = cast(
            "bytes",
            dataset.dump(
                format_=rdf.Format.TURTLE,
                prefixes={"ex": rdf.Iri("http://example.com/")},
            ),
        ).decode("utf-8")
        assert (
            output
            == "@prefix ex: <http://example.com/> .\nex:subject ex:predicate ex:object .\n"
        )

    def test_dump_to_bytes(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        output = cast("bytes", dataset.dump(format_=rdf.Format.NQUADS)).decode("utf-8")
        assert (
            output
            == "<http://example.com/subject> <http://example.com/predicate> <http://example.com/object> .\n"
        )

    def test_dump_to_file(self, dataset: rdf.Dataset, tmp_path: Path) -> None:
        dataset.add(self._TestData.QUAD)
        output_file_path = tmp_path / "temp.nq"
        output = dataset.dump(format_=rdf.Format.NQUADS, output=output_file_path)
        assert output is None
        assert output_file_path.is_file()
        with output_file_path.open() as output_file:
            assert (
                output_file.read()
                == "<http://example.com/subject> <http://example.com/predicate> <http://example.com/object> .\n"
            )

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_is_empty(self, dataset: rdf.Dataset) -> None:
        assert dataset.is_empty

    def test_iter(self, dataset: rdf.Dataset) -> None:
        assert len(tuple(dataset)) == 0
        dataset.add(self._TestData.QUAD)
        assert len(tuple(dataset)) == 1

    def test_len(self, dataset: rdf.Dataset) -> None:
        assert len(dataset) == 0
        dataset.add(self._TestData.QUAD)
        assert len(dataset) == 1
        dataset.add(self._TestData.QUAD)
        assert len(dataset) == 1

    # @pytest.mark.skipif("CI" in os.environ, reason="don't run store tests in CI")
    def test_load_from_file(self, dataset: rdf.Dataset) -> None:
        assert dataset.is_empty
        dataset.load(
            format_=rdf.Format.TURTLE, input_=Path(__file__).parent / "example.ttl"
        )
        assert not dataset.is_empty

    def test_match_empty(self, dataset: rdf.Dataset) -> None:
        assert len(tuple(dataset.match())) == 0

    def test_match_exact(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        matches = tuple(dataset.match(*self._TestData.QUAD))
        assert len(matches) == 1
        assert matches[0] == self._TestData.QUAD

    def test_match_mismatch(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert (
            len(
                tuple(
                    dataset.match(
                        self._TestData.QUAD.subject,
                        self._TestData.QUAD.predicate,
                        self._TestData.BLANK_NODE_OBJECT,
                    )
                )
            )
            == 0
        )

    def test_match_wildcard(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        matches = tuple(
            dataset.match(self._TestData.QUAD.subject, self._TestData.QUAD.predicate)
        )
        assert len(matches) == 1
        assert matches[0] == self._TestData.QUAD

    def test_remove(self, dataset: rdf.Dataset) -> None:
        dataset.remove(self._TestData.QUAD)
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove(
            rdf.Quad(
                self._TestData.QUAD.subject,
                self._TestData.QUAD.predicate,
                self._TestData.BLANK_NODE_OBJECT,
            )
        )
        assert not dataset.is_empty
        dataset.remove(self._TestData.QUAD)
        assert dataset.is_empty

    def test_remove_matches_exact(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove_matches(*self._TestData.QUAD)
        assert dataset.is_empty

    def test_remove_matches_graph(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove_matches(graph=self._TestData.QUAD.graph)
        assert dataset.is_empty

    def test_remove_matches_mismatch(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove_matches(
            self._TestData.QUAD.subject,
            self._TestData.QUAD.predicate,
            self._TestData.BLANK_NODE_OBJECT,
        )
        assert not dataset.is_empty

    def test_remove_matches_object(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove_matches(
            object_=self._TestData.QUAD.object_,
        )
        assert dataset.is_empty

    def test_remove_matches_predicate(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove_matches(
            predicate=self._TestData.QUAD.predicate,
        )
        assert dataset.is_empty

    def test_remove_matches_subject(self, dataset: rdf.Dataset) -> None:
        dataset.add(self._TestData.QUAD)
        assert not dataset.is_empty
        dataset.remove_matches(
            subject=self._TestData.QUAD.subject,
        )
        assert dataset.is_empty
