from pathlib import Path
from collections.abc import Iterable

from graphs2go.models import rdf
from graphs2go.models.rdf.oxigraph_dataset import OxigraphDataset
from tests.graphs2go_tests.models.rdf.dataset_test import DatasetTest


class OxigraphDatasetTest(DatasetTest):
    def dataset(self, tmp_path: Path) -> Iterable[rdf.Dataset]:
        yield OxigraphDataset()
