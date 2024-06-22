from returns.maybe import Some

from graphs2go.models import rdf
from graphs2go.models.compression_method import CompressionMethod

RDF_FILE_FORMATS_DEFAULT = (
    rdf.FileFormat(
        compression_method=Some(CompressionMethod.BROTLI),
        format_=rdf.Format.NTRIPLES,
    ),
    rdf.FileFormat(format_=rdf.Format.TURTLE),
)
