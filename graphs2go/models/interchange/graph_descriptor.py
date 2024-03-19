from dataclasses import dataclass

import rdflib


@dataclass(frozen=True)
class GraphDescriptor:
    """
    A picklable dataclass identifying an interchange graph. It can be used to open an InterchangeGraphLoader.
    """

    identifier: rdflib.URIRef
