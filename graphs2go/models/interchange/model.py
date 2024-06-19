from abc import ABC
from datetime import date, datetime
from typing import Self

from rdflib import DCTERMS, Literal, URIRef
from returns.maybe import Maybe

from graphs2go.models import rdf


class Model(rdf.NamedModel, ABC):
    class Builder(rdf.NamedModel.Builder, ABC):
        def set_created(self, created: date | datetime) -> Self:
            self._resource_builder.set(DCTERMS.created, Literal(created))
            return self

        def set_modified(self, modified: date | datetime) -> Self:
            self._resource_builder.set(DCTERMS.modified, Literal(modified))
            return self

        def set_source(self, source: URIRef) -> Self:
            return self._resource_builder.set(DCTERMS.source, source)

    @property
    def created(self) -> Maybe[datetime]:
        return self.resource.optional_value(
            DCTERMS.created, rdf.Resource.ValueMappers.datetime
        )

    @property
    def modified(self) -> Maybe[datetime]:
        return self.resource.optional_value(
            DCTERMS.modified, rdf.Resource.ValueMappers.datetime
        )
