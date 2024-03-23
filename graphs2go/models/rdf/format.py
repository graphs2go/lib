from enum import Enum


class Format(Enum):
    NQUADS = "nq", True, True
    NTRIPLES = "nt", True, False
    TRIG = "trig", False, True
    TURTLE = "ttl", False, False

    def __init__(
        self,
        file_extension: str,
        line_oriented: bool,  # noqa: FBT001
        supports_quads: bool,  # noqa: FBT001
    ):
        self.file_extension = file_extension
        self.line_oriented = line_oriented
        self.supports_quads = supports_quads
