from collections.abc import Callable
from logging import Logger
import os
from pathlib import Path
from typing import TypeVar


ReleaseT = TypeVar("ReleaseT")


def find_releases(
    *,
    logger: Logger,
    release_directory_path: Path,
    release_factory: Callable[[Path], ReleaseT]
) -> tuple[ReleaseT, ...]:
    """
    Find releases (of e.g., SNOMED-CT, UMLS, et al.) in the release_directory path or its subdirectories.

    release_factory is called with a candidate directory path. It should return a release object or throw ValueError.
    """

    releases: list[ReleaseT] = []

    try:
        releases.append(release_factory(release_directory_path))
        logger.info("release directory %s is a release itself", release_directory_path)
    except ValueError:
        logger.info(
            "release directory %s is not a release itself, scanning subdirectories",
            release_directory_path,
        )

        for subdir_name in os.listdir(release_directory_path):
            release_subdirectory_path = release_directory_path / subdir_name
            try:
                releases.append(release_factory(release_subdirectory_path))
            except ValueError:
                logger.debug(
                    "directory %s is not a release, skipping", release_subdirectory_path
                )

    return tuple(releases)
