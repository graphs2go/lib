from pathlib import Path

import dotenv


def load_dotenv() -> None:
    repository_root_dir_path = Path(__file__).parent.parent.parent.parent

    for dotenv_file_path in (
        repository_root_dir_path / ".env.local",
        repository_root_dir_path / ".env.docker",
    ):
        if dotenv_file_path.is_file():
            dotenv.load_dotenv(dotenv_file_path)
            return
