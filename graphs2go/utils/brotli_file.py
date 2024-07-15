from collections.abc import Buffer
from io import RawIOBase
from pathlib import Path
from typing import Literal, final, override

import brotli


@final
class BrotliFile(RawIOBase):
    """
    Write Brotli-compressed files. Similar to gzip.GzipFile or bz2.BzipFile.

    This is a minimal, write-only implementation, not a full implementation of IO[bytes].
    It is designed to support serialization from rdflib and no more.
    """

    def __init__(
        self,
        filename: Path | str,
        mode: Literal["w", "wb"],  # noqa: ARG002
        brotli_mode: int = brotli.MODE_GENERIC,
        lgblock: int = 0,
        lgwin: int = 22,
        quality: int = 11,
    ):
        self.__compressor = brotli.Compressor(
            mode=brotli_mode, lgblock=lgblock, lgwin=lgwin, quality=quality
        )
        self.__underlying_file = Path(filename).open("wb")  # noqa: SIM115

    @override
    def close(self) -> None:
        compressed_b = self.__compressor.finish()
        self.__underlying_file.write(compressed_b)
        self.__underlying_file.close()

    @override
    def write(self, b: Buffer) -> int:
        compressed_b = self.__compressor.process(b)
        self.__underlying_file.write(compressed_b)
        return len(b)  # type: ignore
