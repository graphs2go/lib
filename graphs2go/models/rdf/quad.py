from typing import NamedTuple

from .blank_node import BlankNode
from .iri import Iri
from .literal import Literal

Quad_Graph = BlankNode | Iri | None
Quad_Object = BlankNode | Iri | Literal
Quad_Predicate = Iri
Quad_Subject = BlankNode | Iri


class Quad(NamedTuple):
    subject: Quad_Subject
    predicate: Quad_Predicate
    object_: Quad_Object
    graph: Quad_Graph = None
