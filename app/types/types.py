from enum import Enum
from pathlib import Path


class PathEnum(Path, Enum):
    """
    Enum where members are also (and must be) Path objects
    """

    def __new__(cls, *values):
        "values must already be of type `Path` or `str`"
        if len(values) != 1:
            raise TypeError("PathEnum requires exactly one argument")
        if not isinstance(values[0], (str, Path)):
            raise TypeError("%r is not a valid path or string" % (values[0],))
        value = Path(values[0])
        member = Path.__new__(cls, value)
        member._value_ = value
        return member

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """
        Return the lower-cased version of the member name.
        """
        return name.lower()


__all__: list[str] = ["PathEnum"]
