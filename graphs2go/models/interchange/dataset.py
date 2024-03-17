from dataclasses import dataclass

from rdflib import URIRef


@dataclass(frozen=True)
class Dataset:
    identifier: URIRef
