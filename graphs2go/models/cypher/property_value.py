from __future__ import annotations

from datetime import date, datetime

PropertyValue = (
    bool | date | datetime | float | int | None | str | tuple["PropertyValue", ...]
)
