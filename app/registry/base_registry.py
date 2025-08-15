"""Module documentation for `app/registry/base_registry.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from typing import Generic, Iterable, List, MutableMapping, TypeVar

ItemT = TypeVar("ItemT")


class RegistryError(RuntimeError):
    """Summary of `RegistryError`."""


class ItemNotFound(KeyError):
    """Summary of `ItemNotFound`."""


class BaseRegistry(Generic[ItemT]):
    """Summary of `BaseRegistry`.

    Attributes:
        cache: Description of `cache`.
    """

    def __init__(self) -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.

        """
        self.cache: MutableMapping[str, ItemT] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Summary of `_load_all`.

        Args:
            self: Description of self.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError

    def _card(self, item: ItemT) -> dict:
        """Summary of `_card`.

        Args:
            self: Description of self.
            item (ItemT): Description of item.

        Returns:
            dict: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError

    def get(self, name: str) -> ItemT:
        """Summary of `get`.

        Args:
            self: Description of self.
            name (str): Description of name.

        Returns:
            ItemT: Description of return value.

        Raises:
            ItemNotFound: Condition when this is raised.

        """
        try:
            return self.cache[name]
        except KeyError as e:
            raise ItemNotFound(name) from e

    def has(self, name: str) -> bool:
        """Summary of `has`.

        Args:
            self: Description of self.
            name (str): Description of name.

        Returns:
            bool: Description of return value.

        """
        return name in self.cache

    def keys(self) -> List[str]:
        """Summary of `keys`.

        Args:
            self: Description of self.

        Returns:
            List[str]: Description of return value.

        """
        return list(self.cache.keys())

    def items(self) -> Iterable[tuple[str, ItemT]]:
        """Summary of `items`.

        Args:
            self: Description of self.

        Returns:
            Iterable[tuple[str, ItemT]]: Description of return value.

        """
        return self.cache.items()

    def cards(self) -> list[dict]:
        """Summary of `cards`.

        Args:
            self: Description of self.

        Returns:
            list[dict]: Description of return value.

        """
        return [self._card(item) for item in self.cache.values()]
