"""Self-balancing AVL tree for predictable city lookup."""

from dataclasses import dataclass
from typing import Iterator

from .city import City


@dataclass(slots=True)
class _Node:
    city: City
    left: "_Node | None" = None
    right: "_Node | None" = None
    height: int = 1


class AVLTree:
    """Map city names to records while maintaining an AVL balance invariant."""

    def __init__(self) -> None:
        self._root: _Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    @property
    def height(self) -> int:
        return self._height(self._root)

    def insert(self, city: City) -> City | None:
        """Insert or update ``city`` and return the replaced record if present."""

        previous = self.find(city.name)
        self._root = self._insert(self._root, city)
        if previous is None:
            self._size += 1
        return previous

    def find(self, name: str) -> City | None:
        key = self._normalize_key(name)
        node = self._root
        while node is not None:
            if key == node.city.key:
                return node.city
            node = node.left if key < node.city.key else node.right
        return None

    def delete(self, name: str) -> City | None:
        """Delete ``name`` and return its record, or ``None`` when absent."""

        key = self._normalize_key(name)
        previous = self.find(name)
        if previous is None:
            return None
        self._root = self._delete(self._root, key)
        self._size -= 1
        return previous

    def inorder(self) -> Iterator[City]:
        stack: list[_Node] = []
        node = self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node.city
            node = node.right

    def validate(self) -> bool:
        """Check ordering, stored heights, balance factors, and size."""

        def audit(node: _Node | None, low: str | None, high: str | None) -> tuple[bool, int, int]:
            if node is None:
                return True, 0, 0
            key = node.city.key
            if (low is not None and key <= low) or (high is not None and key >= high):
                return False, 0, 0
            left_ok, left_height, left_count = audit(node.left, low, key)
            right_ok, right_height, right_count = audit(node.right, key, high)
            actual_height = 1 + max(left_height, right_height)
            valid = (
                left_ok
                and right_ok
                and node.height == actual_height
                and abs(left_height - right_height) <= 1
            )
            return valid, actual_height, 1 + left_count + right_count

        valid, _, count = audit(self._root, None, None)
        return valid and count == self._size

    def _insert(self, node: _Node | None, city: City) -> _Node:
        if node is None:
            return _Node(city)
        if city.key < node.city.key:
            node.left = self._insert(node.left, city)
        elif city.key > node.city.key:
            node.right = self._insert(node.right, city)
        else:
            node.city = city
            return node
        return self._rebalance(node)

    def _delete(self, node: _Node | None, key: str) -> _Node | None:
        if node is None:
            return None
        if key < node.city.key:
            node.left = self._delete(node.left, key)
        elif key > node.city.key:
            node.right = self._delete(node.right, key)
        elif node.left is None:
            return node.right
        elif node.right is None:
            return node.left
        else:
            successor = self._minimum(node.right)
            node.city = successor.city
            node.right = self._delete(node.right, successor.city.key)
        return self._rebalance(node)

    @classmethod
    def _rebalance(cls, node: _Node) -> _Node:
        cls._update_height(node)
        balance = cls._height(node.left) - cls._height(node.right)
        if balance > 1:
            if cls._height(node.left.left) < cls._height(node.left.right):
                node.left = cls._rotate_left(node.left)
            return cls._rotate_right(node)
        if balance < -1:
            if cls._height(node.right.right) < cls._height(node.right.left):
                node.right = cls._rotate_right(node.right)
            return cls._rotate_left(node)
        return node

    @classmethod
    def _rotate_left(cls, root: _Node) -> _Node:
        pivot = root.right
        if pivot is None:
            raise RuntimeError("left rotation requires a right child")
        root.right = pivot.left
        pivot.left = root
        cls._update_height(root)
        cls._update_height(pivot)
        return pivot

    @classmethod
    def _rotate_right(cls, root: _Node) -> _Node:
        pivot = root.left
        if pivot is None:
            raise RuntimeError("right rotation requires a left child")
        root.left = pivot.right
        pivot.right = root
        cls._update_height(root)
        cls._update_height(pivot)
        return pivot

    @staticmethod
    def _minimum(node: _Node) -> _Node:
        while node.left is not None:
            node = node.left
        return node

    @staticmethod
    def _height(node: _Node | None) -> int:
        return node.height if node is not None else 0

    @classmethod
    def _update_height(cls, node: _Node) -> None:
        node.height = 1 + max(cls._height(node.left), cls._height(node.right))

    @staticmethod
    def _normalize_key(name: str) -> str:
        key = name.strip().casefold()
        if not key:
            raise ValueError("city name must not be empty")
        return key
