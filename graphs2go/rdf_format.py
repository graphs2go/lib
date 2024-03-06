from enum import Enum


class RdfFormat(Enum):
    NQUADS = "nquads"
    NTRIPLES = "ntriples"
    TRIG = "trig"
    TURTLE = "turtle"

    @property
    def line_oriented(self) -> bool:
        return self in (RdfFormat.NQUADS, RdfFormat.NTRIPLES)

    def __str__(self):
        return self.value

    @property
    def supports_quads(self) -> bool:
        return self in (RdfFormat.NQUADS, RdfFormat.TRIG)
