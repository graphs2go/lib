from rdflib import Namespace as _Namespace, DCTERMS, RDF, RDFS, SKOS  # noqa: F401
from rdflib.namespace import DefinedNamespace as _DefinedNamespace

from .dash import DASH
from .interchange import INTERCHANGE
from .skosxl import SKOSXL

NAMESPACES: dict[str, type[_DefinedNamespace] | _Namespace] = {
    "dash": DASH,
    "interchange": INTERCHANGE,
    "skos": "SKOS",
    "skosxl": SKOSXL,
}
