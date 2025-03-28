from abc import ABC
from dataclasses import dataclass


class Store(ABC):  # noqa: B024
    @dataclass(frozen=True)
    class Identifier:
        """
        Store identifier. Use a bespoke data structure instead of an arbitrary IRI to support consumers e.g., forming an
        Oxigraph directory path from <base directory> / <namespace> / <name>
        """

        name: str
        namespace: str
