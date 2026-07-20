"""Domain model shared by the route-planning data structures."""

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class City:
    """A city and the route-planning values associated with it."""

    name: str
    latitude: float
    longitude: float
    population: int
    distance: float

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        if not normalized_name:
            raise ValueError("city name must not be empty")
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")
        if self.population < 0:
            raise ValueError("population must not be negative")
        if not math.isfinite(self.distance) or self.distance < 0:
            raise ValueError("distance must be a finite non-negative value")

        object.__setattr__(self, "name", normalized_name)

    @property
    def key(self) -> str:
        """Return a case-insensitive key while preserving the display name."""

        return self.name.casefold()
