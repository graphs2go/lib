from abc import ABC
from datetime import date, datetime
from typing import Self

from returns.maybe import Maybe
from returns.pipeline import is_successful

from graphs2go.models import rdf
from graphs2go.namespaces import DCTERMS


class Model(rdf.NamedModel, ABC):
    class Builder(rdf.NamedModel.Builder, ABC):
        def set_created(self, created: date | datetime | None) -> Self:
            if created is not None:
                self._resource_builder.set(DCTERMS.created, rdf.Literal(created))
            return self

        def set_modified(self, modified: date | datetime | None) -> Self:
            if modified is not None:
                self._resource_builder.set(DCTERMS.modified, rdf.Literal(modified))
            return self

        def set_source(self, source: rdf.Iri | None) -> Self:
            if source is not None:
                self._resource_builder.set(DCTERMS.source, source)
            return self

    @property
    def created(self) -> Maybe[datetime]:
        return self.resource.value(DCTERMS.created).bind(
            lambda value: value.to_datetime()
        )

    @property
    def is_reified(self) -> bool:
        return is_successful(self.created) or is_successful(self.modified)

    @property
    def modified(self) -> Maybe[datetime]:
        return self.resource.value(DCTERMS.modified).bind(
            lambda value: value.to_datetime()
        )
