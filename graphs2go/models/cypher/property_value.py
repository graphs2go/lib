from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

PropertyValue = (
    bool
    | date
    | datetime
    | Decimal
    | float
    | int
    | None
    | str
    | tuple["PropertyValue", ...]
)
