from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Format(Enum):
    NQUADS = "nq", True, True
    NTRIPLES = "nt", True, False
    TRIG = "trig", False, True
    TURTLE = "ttl", False, False

    def __init__(self, file_extension: str, line_oriented: bool, supports_quads: bool):
        self.file_extension = file_extension
        self.line_oriented = line_oriented
        self.supports_quads = supports_quads

    @classmethod
    def guess(cls, file_path: Path) -> Format:
        file_path_suffixes = list(file_path.suffixes)

        if len(file_path_suffixes) == 0:
            raise ValueError("unsupported RDF format: " + str(file_path))

        match file_path_suffixes[-1].lower():
            case ".gz":
                file_path_suffixes.pop()

        match file_path_suffixes[-1].lower():
            case ".nt":
                return cls.NTRIPLES
            case ".ttl":
                return cls.TURTLE
            case other:
                raise ValueError("unsupported RDF format: " + other)

    def __new__(
        cls,
        file_extension: str,
        line_oriented: bool,  # noqa: ARG004
        supports_quads: bool,  # noqa: ARG004
    ):
        obj = object.__new__(cls)
        obj._value_ = file_extension
        return obj

    def __str__(self):
        return self.file_extension
