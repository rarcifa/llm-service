"""
base_registry.py

Defines a lightweight, typed base class for registries that cache named items.
Subclasses implement `_load_all()` to populate `.cache` and `_card()` to expose
metadata for UI/diagnostics.

Typical usage:
    class MyRegistry(BaseRegistry[MyItem]):
        def _load_all(self) -> None: ...
        def _card(self, item: MyItem) -> dict: ...

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from __future__ import annotations
from typing import Dict, Generic, Iterable, List, Mapping, MutableMapping, TypeVar

ItemT = TypeVar("ItemT")


class RegistryError(RuntimeError):
    """Generic registry error."""


class ItemNotFound(KeyError):
    """Raised when a requested item is not found in the registry."""


class BaseRegistry(Generic[ItemT]):
    """
    Base class for name → item registries with in-memory caching.

    Attributes:
        cache (dict[str, ItemT]): Loaded items keyed by name.
    """

    def __init__(self) -> None:
        self.cache: MutableMapping[str, ItemT] = {}
        self._load_all()

    # --- required subclass hooks ------------------------------------------------

    def _load_all(self) -> None:
        """
        Populate `self.cache` with all available items.
        Subclasses must implement this method.
        """
        raise NotImplementedError

    def _card(self, item: ItemT) -> dict:
        """
        Return a JSON-serializable metadata card for `item`.
        Subclasses must implement this method.
        """
        raise NotImplementedError

    # --- shared API -------------------------------------------------------------

    def get(self, name: str) -> ItemT:
        """
        Retrieve an item by name.

        Args:
            name: Item key.

        Returns:
            The cached item.

        Raises:
            ItemNotFound: If the item is not present.
        """
        try:
            return self.cache[name]
        except KeyError as e:
            raise ItemNotFound(name) from e

    def has(self, name: str) -> bool:
        """Return True if an item with `name` exists."""
        return name in self.cache

    def keys(self) -> List[str]:
        """List of item names in the registry."""
        return list(self.cache.keys())

    def items(self) -> Iterable[tuple[str, ItemT]]:
        """Iterator over (name, item) pairs."""
        return self.cache.items()

    def cards(self) -> list[dict]:
        """
        Build metadata cards for all items (e.g., for UIs and logs).

        Returns:
            A list of JSON-serializable dicts.
        """
        return [self._card(item) for item in self.cache.values()]
