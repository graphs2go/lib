from pathlib import Path

import dotenv


def load_dotenv() -> None:
    for dotenv_file_path in (
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent.parent / ".env.docker",
    ):
        if dotenv_file_path.is_file():
            dotenv.load_dotenv(dotenv_file_path)
