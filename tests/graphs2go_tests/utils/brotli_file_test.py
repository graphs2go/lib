from pathlib import Path

import brotli
from rdflib import Graph

from graphs2go.models import rdf
from graphs2go.utils.brotli_file import BrotliFile


def test_rdflib_serialize(tmp_path: Path) -> None:
    graph = Graph()
    graph.add(
        (
            rdf.Iri("http://example.com/subject"),
            rdf.Iri("http://example.com/predicate"),
            rdf.Iri("http://example.com/object"),
        )
    )
    graph_ttl = graph.serialize(format="ttl")
    assert graph_ttl

    brotli_file_path = tmp_path / "graph.ttl.br"
    with BrotliFile(brotli_file_path, "wb") as brotli_file:
        graph.serialize(destination=brotli_file, encoding="utf-8", format="ttl")  # type: ignore
    with brotli_file_path.open("rb") as brotli_file:
        brotli_ttl = brotli.decompress(brotli_file.read()).decode("utf-8")
        assert brotli_ttl == graph_ttl
