from enum import Enum


class CompressionMethod(Enum):
    BROTLI = "br"
    BZIP2 = "bz2"
    GZIP = "gz"

    def __init__(
        self,
        file_extension: str,
    ):
        self.file_extension = file_extension

    def __new__(cls, file_extension: str):
        obj = object.__new__(cls)
        obj._value_ = file_extension
        return obj

    def __str__(self):
        return self.file_extension
