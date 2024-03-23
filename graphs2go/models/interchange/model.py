from datetime import date, datetime
from graphs2go.models import rdf
from typing import Self
from rdflib import DCTERMS, Literal


class Model(rdf.Model):
    class Builder(rdf.Model.Builder):
        def set_created(self, created: date | datetime) -> Self:
            self._resource.set(DCTERMS.created, Literal(created))
            return self

        def set_modified(self, modified: date | datetime | None) -> Self:
            if modified:
                self._resource.set(DCTERMS.modified, Literal(modified))
            else:
                self._resource.remove(DCTERMS.modified)
            return self
