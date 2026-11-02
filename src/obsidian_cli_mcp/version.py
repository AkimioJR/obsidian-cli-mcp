import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Version:
    """Semantic version representation (major.minor.patch) with comparison support.

    Supports parsing versions from strings like "1.14.5", "v1.14.5",
    "1.14.5 (installer 1.14.5)", and comparisons with Version instances or version strings.
    """

    major: int
    minor: int = 0
    patch: int = 0

    _REGEX = re.compile(r"(?:v|version\s*)?(\d+)\.(\d+)(?:\.(\d+))?", re.IGNORECASE)

    @classmethod
    def parse(cls, raw: str) -> "Version":
        """Parse a version string into a Version instance."""
        if not isinstance(raw, str):
            raise TypeError(f"Expected str, got {type(raw).__name__}")
        m = cls._REGEX.search(raw.strip())
        if not m:
            raise ValueError(f"Invalid version string: {raw!r}")
        major = int(m.group(1))
        minor = int(m.group(2))
        patch = int(m.group(3)) if m.group(3) is not None else 0
        return cls(major=major, minor=minor, patch=patch)

    @classmethod
    def try_parse(cls, raw: str | None) -> "Version | None":
        """Safely parse a version string, returning None on failure or empty input."""
        if not raw:
            return None
        try:
            return cls.parse(raw)
        except (ValueError, TypeError):
            return None

    def _cmp_tuple(self) -> tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def _to_other_tuple(self, other: Any) -> tuple[int, int, int] | Any:
        if isinstance(other, Version):
            return other._cmp_tuple()
        if isinstance(other, str):
            try:
                return Version.parse(other)._cmp_tuple()
            except ValueError:
                return NotImplemented
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        t = self._to_other_tuple(other)
        if t is NotImplemented:
            return False
        return self._cmp_tuple() == t

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Any) -> bool:
        t = self._to_other_tuple(other)
        if t is NotImplemented:
            return NotImplemented
        return self._cmp_tuple() < t

    def __le__(self, other: Any) -> bool:
        t = self._to_other_tuple(other)
        if t is NotImplemented:
            return NotImplemented
        return self._cmp_tuple() <= t

    def __gt__(self, other: Any) -> bool:
        t = self._to_other_tuple(other)
        if t is NotImplemented:
            return NotImplemented
        return self._cmp_tuple() > t

    def __ge__(self, other: Any) -> bool:
        t = self._to_other_tuple(other)
        if t is NotImplemented:
            return NotImplemented
        return self._cmp_tuple() >= t

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


__all__ = ["Version"]
