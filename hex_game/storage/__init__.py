"""
Moduł zarządzania danymi
"""

from .game_storage import GameStorage, MemoryStorage, FileStorage

__all__ = ['GameStorage', 'MemoryStorage', 'FileStorage']