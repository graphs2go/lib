from enum import Enum


class Format(Enum):
    NQUADS = "nquads"
    NTRIPLES = "ntriples"
    TRIG = "trig"
    TURTLE = "turtle"

    @property
    def line_oriented(self) -> bool:
        return self in (Format.NQUADS, Format.NTRIPLES)

    def __str__(self):
        return self.value

    @property
    def supports_quads(self) -> bool:
        return self in (Format.NQUADS, Format.TRIG)
