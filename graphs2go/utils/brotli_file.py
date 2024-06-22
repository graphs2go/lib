from io import RawIOBase
from pathlib import Path
from typing import Literal

import brotli


class BrotliFile(RawIOBase):
    """
    Write Brotli-compressed files. Similar to gzip.GzipFile or bz2.BzipFile.

    This is a minimal, write-only implementation, not a full implementation of IO[bytes].
    It is designed to support serialization from rdflib and no more.
    """

    def __init__(
        self,
        filename: Path | str,
        mode: Literal["w", "wb"],
        brotli_mode: int = brotli.MODE_GENERIC,
    ):  # noqa: ARG002
        self.__compressor = brotli.Compressor(mode=brotli_mode)
        self.__underlying_file = Path(filename).open("wb")  # noqa: SIM115

    def close(self) -> None:
        compressed_b = self.__compressor.finish()
        self.__underlying_file.write(compressed_b)
        self.__underlying_file.close()

    def write(self, b: bytes) -> int:
        compressed_b = self.__compressor.process(b)
        self.__underlying_file.write(compressed_b)
        return len(b)
