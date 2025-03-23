from collections.abc import Iterable
from typing import TypeVar

from returns.pipeline import is_successful
from returns.result import Result

_ErrorType = TypeVar("_ErrorType", covariant=True)  # noqa: PLC0105
_ValueType = TypeVar("_ValueType", covariant=True)  # noqa: PLC0105


def success_values(
    results: Iterable[Result[_ValueType, _ErrorType]],
) -> Iterable[_ValueType]:
    """
    Given an Iterable of Results, yield the unwrapped successes.
    """
    for result in results:
        if is_successful(result):
            yield result.unwrap()
