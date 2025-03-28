from pathlib import Path
from typing import TYPE_CHECKING, final

import stringcase

from graphs2go.models import cypher

if TYPE_CHECKING:
    from io import TextIOWrapper


@final
class DirectoryLoader:
    def __init__(self, *, directory_path: Path):
        self.__directory_path = directory_path
        self.__directory_path.mkdir(parents=True, exist_ok=True)
        self.__open_files_by_name: dict[str, TextIOWrapper] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ANN001
        self.close()

    def close(self) -> None:
        for open_file in self.__open_files_by_name.values():
            open_file.close()

    def load(self, cypher_statement: cypher.Statement) -> None:
        assert cypher_statement.__class__.__name__.endswith("Statement")
        file_name = (
            stringcase.snakecase(
                cypher_statement.__class__.__name__[: -len("Statement")]
            )
            + ".cypher"
        )
        open_file = self.__open_files_by_name.get(file_name)
        if open_file is None:
            self.__open_files_by_name[file_name] = open_file = Path.open(
                self.__directory_path / file_name, "w+"
            )
        open_file.write(cypher_statement.cypher_str + "\n\n")
