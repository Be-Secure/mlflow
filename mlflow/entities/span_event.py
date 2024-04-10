import sys
import time
import traceback
from dataclasses import dataclass, field
from typing import Dict, Sequence, Union

from mlflow.entities._mlflow_object import _MlflowObject

_AttrValueType = Union[str, int, float, bool, bytes]


@dataclass
class SpanEvent(_MlflowObject):
    """
    An event that records a specific occurrences or moments in time
    during a span, such as an exception being thrown.

    Args:
        name: Name of the event.
        timestamp:  The exact time the event occurred, measured in microseconds.
            If not provided, the current time will be used.
        attributes: A collection of key-value pairs representing detailed
            attributes of the event, such as the exception stack trace.
            Attributes value must be one of ``[str, int, float, bool, bytes]``
            or a sequence of these types.
    """

    name: str
    # Use current time if not provided. We need to use default factory otherwise
    # the default value will be fixed to the build time of the class.
    timestamp: int = field(default_factory=lambda: int(time.time() * 1e6))
    attributes: Dict[str, Union[_AttrValueType, Sequence[_AttrValueType]]] = field(
        default_factory=dict
    )

    @classmethod
    def from_exception(cls, exception: Exception):
        "Create a span event from an exception."

        stack_trace = cls._get_stacktrace(exception)
        return cls(
            name="exception",
            attributes={
                "exception.message": str(exception),
                "exception.type": exception.__class__.__name__,
                "exception.stacktrace": stack_trace,
            },
        )

    @staticmethod
    def _get_stacktrace(error: BaseException) -> str:
        """Get the stacktrace of the parent error."""
        msg = repr(error)
        try:
            if sys.version_info < (3, 10):
                tb = traceback.format_exception(error.__class__, error, error.__traceback__)
            else:
                tb = traceback.format_exception(error)
            return (msg + "\n\n".join(tb)).strip()
        except Exception:
            return msg