from abc import abstractmethod
from pathlib import Path

from pyparsing import ABC


class DirectoryLoader(ABC):
    """
    Abstract base class for loaders that write files to a directory on the local file system.
    """

    def __init__(self, *, directory_path: Path):
        self.__directory_path = directory_path
        self.__directory_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def close(self) -> None:
        pass

    @property
    def _directory_path(self) -> Path:
        return self.__directory_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()
