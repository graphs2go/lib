from dataclasses import dataclass

from returns.maybe import Maybe, Nothing
from returns.pipeline import is_successful

from graphs2go.models.compression_method import CompressionMethod
from graphs2go.models.rdf.format import Format


@dataclass(frozen=True)
class FileFormat:
    format_: Format
    compression_method: Maybe[CompressionMethod] = Nothing

    @property
    def file_extension(self) -> str:
        if is_successful(self.compression_method):
            return f"{self.format_.file_extension}.{self.compression_method.unwrap().file_extension}"
        return self.format_.file_extension
