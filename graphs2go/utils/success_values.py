from collections.abc import Iterable

from returns.pipeline import is_successful
from returns.result import Result


def success_values[ValueType, ErrorType](
    results: Iterable[Result[ValueType, ErrorType]],
) -> Iterable[ValueType]:
    """
    Given an Iterable of Results, yield the unwrapped successes.
    """
    for result in results:
        if is_successful(result):
            yield result.unwrap()
