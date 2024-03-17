from pathlib import Path


def parse_directory_path_config_value(value: str, *, default: Path) -> Path:
    directory_path = Path(value) if value else default

    if not directory_path.is_dir():
        raise ValueError(
            f"directory {directory_path} does not exist or is not a directory"
        )

    return directory_path.absolute()
