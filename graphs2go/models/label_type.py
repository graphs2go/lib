from enum import Enum

from rdflib import SKOS, URIRef

from graphs2go.namespaces.skosxl import SKOSXL


class LabelType(Enum):
    ALTERNATIVE = SKOS.altLabel, SKOSXL.altLabel
    HIDDEN = SKOS.hiddenLabel, SKOSXL.hiddenLabel
    PREFERRED = SKOS.prefLabel, SKOSXL.prefLabel

    def __init__(self, skos_predicate: URIRef, skosxl_predicate: URIRef):
        self.skos_predicate = skos_predicate
        self.skosxl_predicate = skosxl_predicate

    def __new__(cls, *args, **kwds):  # noqa: ANN003, ANN002, ARG004
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
