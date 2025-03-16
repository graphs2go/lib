from collections.abc import Callable
from logging import Logger
from pathlib import Path
from typing import TypeVar

ReleaseT = TypeVar("ReleaseT")


def find_file_releases(
    *,
    logger: Logger,
    release_directory_path: Path,
    release_factory: Callable[[Path], ReleaseT],
) -> tuple[ReleaseT, ...]:
    """
    Find releases (of e.g., SNOMED-CT, UMLS, et al.) in the release_directory path or its subdirectories.

    release_factory is called with a candidate directory path. It should return a release object or throw ValueError.
    """

    release_directory_path = release_directory_path.absolute()
    if not release_directory_path.is_dir():
        raise ValueError(
            "release directory {release_directory_path} is not a directory"
        )

    releases: list[ReleaseT] = []

    for file_name in Path.iterdir(release_directory_path):
        file_path = release_directory_path / file_name
        if not file_path.is_file():
            continue

        try:
            releases.append(release_factory(file_path))
            logger.info("file %s is a release", file_path)
        except ValueError:
            logger.debug("file %s is not a release", file_path)

    return tuple(releases)
