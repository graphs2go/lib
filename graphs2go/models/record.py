from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    stream: str
