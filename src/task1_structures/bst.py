"""Unbalanced binary search tree for city lookup."""

from dataclasses import dataclass
from typing import Iterator

from .city import City


@dataclass(slots=True)
class _Node:
    city: City
    left: "_Node | None" = None
    right: "_Node | None" = None


class BinarySearchTree:
    """Map case-insensitive city names to city records.

    Inserting an existing key replaces its value, matching normal mapping semantics.
    """

    def __init__(self) -> None:
        self._root: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, city: City) -> City | None:
        """Insert a city and return the previous record when its key existed."""

        if self._root is None:
            self._root = _Node(city)
            self._size = 1
            return None

        node = self._root
        while True:
            if city.key == node.city.key:
                previous = node.city
                node.city = city
                return previous
            if city.key < node.city.key:
                if node.left is None:
                    node.left = _Node(city)
                    self._size += 1
                    return None
                node = node.left
            else:
                if node.right is None:
                    node.right = _Node(city)
                    self._size += 1
                    return None
                node = node.right

    def find(self, name: str) -> City | None:
        """Return the city with ``name``, or ``None`` when absent."""

        key = self._normalize_key(name)
        node = self._root
        while node is not None:
            if key == node.city.key:
                return node.city
            node = node.left if key < node.city.key else node.right
        return None

    def delete(self, name: str) -> City | None:
        """Delete a key and return its city, or ``None`` when absent."""

        key = self._normalize_key(name)
        parent: _Node | None = None
        node = self._root

        while node is not None and node.city.key != key:
            parent = node
            node = node.left if key < node.city.key else node.right
        if node is None:
            return None

        deleted = node.city
        if node.left is not None and node.right is not None:
            successor_parent = node
            successor = node.right
            while successor.left is not None:
                successor_parent = successor
                successor = successor.left
            node.city = successor.city
            parent, node = successor_parent, successor

        child = node.left if node.left is not None else node.right
        if parent is None:
            self._root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child

        self._size -= 1
        return deleted

    def inorder(self) -> Iterator[City]:
        """Yield cities in case-insensitive name order without recursion."""

        stack: list[_Node] = []
        node = self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node.city
            node = node.right

    @property
    def height(self) -> int:
        """Return node-count height; an empty tree has height zero."""

        if self._root is None:
            return 0
        maximum = 0
        stack = [(self._root, 1)]
        while stack:
            node, depth = stack.pop()
            maximum = max(maximum, depth)
            if node.left is not None:
                stack.append((node.left, depth + 1))
            if node.right is not None:
                stack.append((node.right, depth + 1))
        return maximum

    def validate(self) -> bool:
        """Check ordering and stored-size invariants."""

        previous_key: str | None = None
        count = 0
        for city in self.inorder():
            if previous_key is not None and city.key <= previous_key:
                return False
            previous_key = city.key
            count += 1
        return count == self._size

    @staticmethod
    def _normalize_key(name: str) -> str:
        key = name.strip().casefold()
        if not key:
            raise ValueError("city name must not be empty")
        return key
