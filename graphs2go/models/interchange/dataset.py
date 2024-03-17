from dataclasses import dataclass
from pathlib import Path

from rdflib import URIRef


@dataclass(frozen=True)
class Dataset:
    identifier: URIRef
