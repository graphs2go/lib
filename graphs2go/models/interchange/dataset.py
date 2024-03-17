from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dataset:
    file_path: Path
