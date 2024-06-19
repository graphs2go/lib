from datetime import date, datetime
from typing import Self

from rdflib import DCTERMS, Literal, URIRef

from graphs2go.models import rdf


class Model(rdf.Model):
    class Builder(rdf.Model.Builder):
        def set_created(self, created: date | datetime | None) -> Self:
            return self.set(
                DCTERMS.created, Literal(created) if created is not None else None
            )

        def set_modified(self, modified: date | datetime | None) -> Self:
            return self.set(
                DCTERMS.modified, Literal(modified) if modified is not None else None
            )

        def set_source(self, source: URIRef | None) -> Self:
            return self.set(DCTERMS.source, source)

    @property
    def created(self) -> datetime | None:
        return self._optional_value(DCTERMS.created, self._map_term_to_datetime)

    @property
    def modified(self) -> datetime | None:
        return self._optional_value(DCTERMS.modified, self._map_term_to_datetime)
