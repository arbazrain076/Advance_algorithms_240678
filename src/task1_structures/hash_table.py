"""Separate-chaining hash table with deterministic hashing and resizing."""

from dataclasses import dataclass

from .city import City


@dataclass(frozen=True, slots=True)
class HashStatistics:
    capacity: int
    entries: int
    occupied_buckets: int
    collisions: int
    longest_chain: int

    @property
    def load_factor(self) -> float:
        return self.entries / self.capacity


class CityHashTable:
    """Case-insensitive city lookup using separate chaining.

    FNV-1a is used instead of Python's process-randomised string hash so benchmark
    bucket distributions remain reproducible across runs.
    """

    _MIN_CAPACITY = 8

    def __init__(self, capacity: int = _MIN_CAPACITY, max_load: float = 0.75) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if not 0.25 <= max_load <= 2.0:
            raise ValueError("max_load must be between 0.25 and 2.0")
        normalized_capacity = max(self._MIN_CAPACITY, self._next_power_of_two(capacity))
        self._buckets: list[list[City]] = [[] for _ in range(normalized_capacity)]
        self._size = 0
        self._max_load = max_load

    def __len__(self) -> int:
        return self._size

    def insert(self, city: City) -> City | None:
        """Insert or update a city, returning the previous record if replaced."""

        bucket = self._bucket(city.key)
        for index, current in enumerate(bucket):
            if current.key == city.key:
                bucket[index] = city
                return current

        bucket.append(city)
        self._size += 1
        if self._size / len(self._buckets) > self._max_load:
            self._resize(len(self._buckets) * 2)
        return None

    def find(self, name: str) -> City | None:
        key = self._normalize_key(name)
        return next((city for city in self._bucket(key) if city.key == key), None)

    def delete(self, name: str) -> City | None:
        key = self._normalize_key(name)
        bucket = self._bucket(key)
        for index, city in enumerate(bucket):
            if city.key == key:
                removed = bucket.pop(index)
                self._size -= 1
                if (
                    len(self._buckets) > self._MIN_CAPACITY
                    and self._size / len(self._buckets) < 0.20
                ):
                    self._resize(len(self._buckets) // 2)
                return removed
        return None

    @property
    def statistics(self) -> HashStatistics:
        chain_lengths = [len(bucket) for bucket in self._buckets]
        return HashStatistics(
            capacity=len(self._buckets),
            entries=self._size,
            occupied_buckets=sum(length > 0 for length in chain_lengths),
            collisions=sum(max(0, length - 1) for length in chain_lengths),
            longest_chain=max(chain_lengths, default=0),
        )

    def validate(self) -> bool:
        seen: set[str] = set()
        count = 0
        for bucket_index, bucket in enumerate(self._buckets):
            for city in bucket:
                if city.key in seen or self._index(city.key) != bucket_index:
                    return False
                seen.add(city.key)
                count += 1
        return count == self._size

    def _bucket(self, key: str) -> list[City]:
        return self._buckets[self._index(key)]

    def _index(self, key: str) -> int:
        return self._fnv1a(key) & (len(self._buckets) - 1)

    def _resize(self, capacity: int) -> None:
        old_items = [city for bucket in self._buckets for city in bucket]
        capacity = max(self._MIN_CAPACITY, self._next_power_of_two(capacity))
        self._buckets = [[] for _ in range(capacity)]
        for city in old_items:
            self._bucket(city.key).append(city)

    @staticmethod
    def _fnv1a(text: str) -> int:
        value = 14_695_981_039_346_656_037
        for byte in text.encode("utf-8"):
            value ^= byte
            value = (value * 1_099_511_628_211) & 0xFFFF_FFFF_FFFF_FFFF
        return value

    @staticmethod
    def _normalize_key(name: str) -> str:
        key = name.strip().casefold()
        if not key:
            raise ValueError("city name must not be empty")
        return key

    @staticmethod
    def _next_power_of_two(value: int) -> int:
        return 1 << (value - 1).bit_length()
