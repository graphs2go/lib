from __future__ import annotations

from typing import TYPE_CHECKING, IO

import pyoxigraph as ox

from graphs2go.models.rdf.dataset import Dataset
from graphs2go.models.rdf.oxigraph_adapters import OxigraphAdapters

if TYPE_CHECKING:
    from graphs2go.models.rdf.iri import Iri
    from graphs2go.models.rdf.format import Format
    from collections.abc import Iterable

    from graphs2go.models.rdf.quad import (
        Quad,
        Quad_Graph,
        Quad_Object,
        Quad_Predicate,
        Quad_Subject,
    )


class OxigraphDataset(Dataset):
    """
    Wrapper for Oxigraph's in-memory implementation of an RDF dataset.

    Adapted from oxrdflib.
    """

    def __init__(self):
        self.__delegate = ox.Dataset()

    def add(self, quad: Quad) -> None:
        self.__delegate.add(OxigraphAdapters.Quad.to_ox(quad))

    def clear(self) -> None:
        self.__delegate.clear()

    def _dump(
        self, *, format_: Format, output: IO[bytes], prefixes: dict[str, Iri]
    ) -> None:
        ox.serialize(
            format=ox.RdfFormat.from_extension(format_.file_extension),
            prefixes={prefix: str(namespace) for prefix, namespace in prefixes.items()},
            input=self.__delegate,
            output=output,
        )

    def _load(self, *, format_: Format, input_: IO[bytes] | IO[str]) -> None:
        for quad in ox.parse(
            input=input_,
            format=ox.RdfFormat.from_extension(format_.file_extension),
        ):
            self.__delegate.add(quad)

    def match(
        self,
        subject: Quad_Subject | None = None,
        predicate: Quad_Predicate | None = None,
        object_: Quad_Object | None = None,
        graph: Quad_Graph = None,
    ) -> Iterable[Quad]:
        subject_ox = (
            OxigraphAdapters.Quad.Subject.to_ox(subject)
            if subject is not None
            else None
        )
        predicate_ox = (
            OxigraphAdapters.Quad.Predicate.to_ox(predicate)
            if predicate is not None
            else None
        )
        object_ox = (
            OxigraphAdapters.Quad.Object.to_ox(object_) if object_ is not None else None
        )
        graph_ox = (
            OxigraphAdapters.Quad.Graph.to_ox(graph) if graph is not None else None
        )

        if (
            graph is not None
            and predicate is None
            and predicate is None
            and object_ is None
        ):
            quads = self.__delegate.quads_for_graph_name(graph_ox)
        elif (
            object_ is not None
            and subject is None
            and predicate is None
            and graph is None
        ):
            quads = self.__delegate.quads_for_object(object_ox)
        elif (
            predicate is not None
            and subject is None
            and object_ is None
            and graph is None
        ):
            quads = self.__delegate.quads_for_predicate(predicate_ox)
        elif (
            subject is not None
            and predicate is None
            and object_ is None
            and graph is None
        ):
            quads = self.__delegate.quads_for_subject(subject_ox)
        else:
            for quad_ox in self.__delegate:
                if subject is not None and subject_ox != quad_ox.subject:
                    continue
                if predicate is not None and predicate_ox != quad_ox.predicate:
                    continue
                if object_ is not None and object_ox != quad_ox.object:
                    continue
                if graph is not None and graph_ox != quad_ox.graph:
                    continue
                yield OxigraphAdapters.Quad.from_ox(quad_ox)
            return

        for quad_ox in quads:
            yield OxigraphAdapters.Quad.from_ox(quad_ox)

    def remove(self, quad: Quad) -> None:
        self.__delegate.discard(OxigraphAdapters.Quad.to_ox(quad))
