from rdflib import Namespace
from rdflib.namespace import DefinedNamespace

from graphs2go.namespaces.dash import DASH
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.namespaces.skosxl import SKOSXL

NAMESPACES: dict[str, type[DefinedNamespace] | Namespace] = {
    "dash": DASH,
    "interchange": INTERCHANGE,
    "skosxl": SKOSXL,
}
