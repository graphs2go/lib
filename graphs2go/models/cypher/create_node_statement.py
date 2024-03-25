from __future__ import annotations
from graphs2go.models.cypher.statement import Statement


class CreateNodeStatement(Statement):
    class Builder(Statement.Builder):
        def build(self) -> CreateNodeStatement:
            pass
