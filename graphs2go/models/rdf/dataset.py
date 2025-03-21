from abc import ABC, abstractmethod
from collections.abc import Iterable

from graphs2go.models.rdf.quad import (
    Quad,
    Quad_Subject,
    Quad_Predicate,
    Quad_Object,
    Quad_Graph,
)


class Dataset(ABC):
    """
    Abstract base class/interface over an RDF dataset (https://www.w3.org/TR/rdf11-datasets/).

    Loosely modeled on Oxigraph's Dataset class (https://pyoxigraph.readthedocs.io/en/stable/model.html#pyoxigraph.Dataset).

    A QuadStore is a persistent implementation of a Dataset.
    """

    @abstractmethod
    def add(self, quad: Quad) -> None:
        """
        Add a quad to the Dataset.
        """

        raise NotImplementedError

    def clear(self) -> None:
        """
        Clear all quads from the Dataset.
        """

        for quad in self.match():
            self.remove(quad)

    def extend(self, quads: Iterable[Quad]) -> None:
        """
        Add zero or more quads to the Dataset.
        """

        for quad in quads:
            self.add(quad)

    @property
    def is_empty(self) -> bool:
        """
        Check if the Dataset has quads or not.
        """

        for _ in self.match():
            return False
        return True

    def __len__(self) -> int:
        """
        The number of quads in the Dataset.
        """

        count = 0
        for _ in self.match():
            count += 1
        return count

    @abstractmethod
    def match(
        self,
        subject: Quad_Subject | None = None,
        predicate: Quad_Predicate | None = None,
        object_: Quad_Object | None = None,
        graph: Quad_Graph = None,
    ) -> Iterable[Quad]:
        """
        Return matching quads in the Dataset.

        If subject is specified, return all quads with that exact subject.
        If subject is unspecified, return quads with any subjects.
        Similar for predicate, object, graph.
        Combinations of parameters are conjunctive (subject = X and predicate = Y).
        """

        raise NotImplementedError

    @abstractmethod
    def remove(self, quad: Quad) -> None:
        """
        Remove a quad from the Dataset.
        """

        raise NotImplementedError()

    def remove_matches(
        self,
        subject: Quad_Subject | None = None,
        predicate: Quad_Predicate | None = None,
        object_: Quad_Object | None = None,
        graph: Quad_Graph = None,
    ) -> None:
        """
        Remove all matching quads from the Dataset.

        The parameters have the same semantics as match.
        """

        for quad in self.match(subject, predicate, object_, graph):
            self.remove(quad)
