from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Statement:
    """
    Abstract base class for Cypher statements.
    """

    value: str

    class Builder(ABC):
        @abstractmethod
        def build(self) -> Statement:
            raise NotImplementedError
