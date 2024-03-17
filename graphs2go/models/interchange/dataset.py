from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dataset:
    store_path: Path
