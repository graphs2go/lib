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

    def __new__(cls, *args, **kwds):  # noqa: ANN003, ANN002, ANN002, ANN003, ARG003
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __str__(self):
        return self.file_extension
