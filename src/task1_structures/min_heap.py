"""Array-backed binary min-heap for selecting the nearest city."""

from .city import City


class MinHeap:
    """Priority queue ordered by distance, then city key for deterministic ties."""

    def __init__(self, cities: list[City] | None = None) -> None:
        self._items = list(cities) if cities is not None else []
        for index in range(len(self._items) // 2 - 1, -1, -1):
            self._sift_down(index)

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def push(self, city: City) -> None:
        """Add a city in O(log n) worst-case time."""

        self._items.append(city)
        self._sift_up(len(self._items) - 1)

    def peek(self) -> City:
        """Return the nearest city without removing it in O(1) time."""

        if not self._items:
            raise IndexError("peek from empty heap")
        return self._items[0]

    def pop(self) -> City:
        """Remove and return the nearest city in O(log n) time."""

        if not self._items:
            raise IndexError("pop from empty heap")
        root = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._sift_down(0)
        return root

    def find(self, name: str) -> City | None:
        """Find a city by name using a linear scan."""

        key = self._normalize_key(name)
        return next((city for city in self._items if city.key == key), None)

    def remove(self, name: str) -> City | None:
        """Remove a named city in O(n) search plus O(log n) repair time."""

        key = self._normalize_key(name)
        index = next(
            (position for position, city in enumerate(self._items) if city.key == key),
            None,
        )
        if index is None:
            return None

        removed = self._items[index]
        last = self._items.pop()
        if index < len(self._items):
            self._items[index] = last
            if index > 0 and self._priority(last) < self._priority(self._items[(index - 1) // 2]):
                self._sift_up(index)
            else:
                self._sift_down(index)
        return removed

    def validate(self) -> bool:
        """Return whether every parent has priority no greater than its children."""

        for index, city in enumerate(self._items):
            left = 2 * index + 1
            right = left + 1
            if left < len(self._items) and self._priority(city) > self._priority(self._items[left]):
                return False
            if right < len(self._items) and self._priority(city) > self._priority(self._items[right]):
                return False
        return True

    def _sift_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._priority(self._items[parent]) <= self._priority(self._items[index]):
                break
            self._items[parent], self._items[index] = self._items[index], self._items[parent]
            index = parent

    def _sift_down(self, index: int) -> None:
        size = len(self._items)
        while True:
            smallest = index
            left = 2 * index + 1
            right = left + 1
            if left < size and self._priority(self._items[left]) < self._priority(
                self._items[smallest]
            ):
                smallest = left
            if right < size and self._priority(self._items[right]) < self._priority(
                self._items[smallest]
            ):
                smallest = right
            if smallest == index:
                return
            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest

    @staticmethod
    def _priority(city: City) -> tuple[float, str]:
        return city.distance, city.key

    @staticmethod
    def _normalize_key(name: str) -> str:
        key = name.strip().casefold()
        if not key:
            raise ValueError("city name must not be empty")
        return key
