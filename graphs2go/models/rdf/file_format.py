from dataclasses import dataclass

from returns.maybe import Maybe, Nothing

from graphs2go.models.compression_method import CompressionMethod
from graphs2go.models.rdf.format import Format


@dataclass(frozen=True)
class FileFormat:
    format_: Format
    compression_method: Maybe[CompressionMethod] = Nothing
