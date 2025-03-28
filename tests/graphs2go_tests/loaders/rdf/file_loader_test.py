from pathlib import Path

import pytest
from returns.maybe import Nothing, Some
from returns.pipeline import is_successful

from graphs2go.loaders.rdf.file_loader import FileLoader
from graphs2go.models import rdf
from graphs2go.models.compression_method import CompressionMethod
from graphs2go.models.rdf.oxigraph_dataset import OxigraphDataset


@pytest.mark.parametrize(
    argnames=("rdf_file_format",),  # noqa: PT006
    argvalues=tuple(
        (rdf.FileFormat(rdf_format, compression_method=compression_method),)
        for rdf_format in rdf.Format
        for compression_method in (
            Nothing,
            *(Some(compression_method) for compression_method in CompressionMethod),
        )
    ),
)
def test_load(
    example_rdf_dataset: rdf.Dataset,
    rdf_file_format: rdf.FileFormat,
    tmp_path: Path,
) -> None:
    rdf_file_path = tmp_path / f"test.{rdf_file_format.file_extension}"
    with FileLoader.create(
        file_format=rdf_file_format,
        file_path=rdf_file_path,
    ) as loader:
        loader.load(example_rdf_dataset)

    assert rdf_file_path.is_file()
    if not is_successful(rdf_file_format.compression_method):
        actual_dataset = OxigraphDataset()
        actual_dataset.load(format_=rdf_file_format.format_, input_=rdf_file_path)
        assert len(actual_dataset) == len(example_rdf_dataset)
