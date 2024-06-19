from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphs2go.models.rdf.resource import Resource


class Model:
    class Builder(ABC):
        def __init__(self, resource_builder: Resource.Builder):
            self.__resource_builder = resource_builder

        @abstractmethod
        def build(self) -> Model:
            raise NotImplementedError

        @property
        def _resource_builder(self) -> Resource.Builder:
            return self.__resource_builder

    def __init__(self, resource: Resource):
        self.__resource = resource

    @property
    def identifier(self) -> Resource.Identifier:
        return self.resource.identifier

    @property
    def resource(self) -> Resource:
        return self.__resource

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(identifier={self.identifier})"
