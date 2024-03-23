from datetime import date, datetime
from typing import Self

from rdflib import DCTERMS, Literal

from graphs2go.models import rdf


class Model(rdf.Model):
    class Builder(rdf.Model.Builder):
        def set_created(self, created: date | datetime | None) -> Self:
            if created:
                self._resource.set(DCTERMS.created, Literal(created))
            else:
                self._resource.remove(DCTERMS.created)
            return self

        def set_modified(self, modified: date | datetime | None) -> Self:
            if modified:
                self._resource.set(DCTERMS.modified, Literal(modified))
            else:
                self._resource.remove(DCTERMS.modified)
            return self

    @property
    def created(self) -> datetime:
        return self._required_value(DCTERMS.created, self._map_term_to_datetime)

    @property
    def modified(self) -> datetime | None:
        return self._optional_value(DCTERMS.modified, self._map_term_to_datetime)
