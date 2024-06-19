from datetime import date, datetime
from typing import Self

from rdflib import DCTERMS, Literal
from returns.maybe import Maybe

from graphs2go.models import rdf


class Model(rdf.Model):
    class Builder(rdf.Model.Builder):
        def set_created(self, created: date | datetime) -> Self:
            self._resource_builder.set(DCTERMS.created, Literal(created))
            return self

        def set_modified(self, modified: date | datetime) -> Self:
            self._resource_builder.set(DCTERMS.modified, Literal(modified))
            return self

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
