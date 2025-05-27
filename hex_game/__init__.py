"""
Pakiet gry HEX

Struktura:
- core/: Główna logika gry (silnik)
- players/: Implementacje różnych typów graczy
- ui/: Interfejsy użytkownika
- storage/: Mechanizmy zapisu/odczytu
- api/: Flask REST API (nowe)
"""

__version__ = "2.0.0"
__author__ = "Student"

from .core.engine import HexEngine, Player, GameState
from .players import BasePlayer, HumanPlayer, ComputerPlayer
from .ui import ConsoleUI
from .storage import GameStorage, MemoryStorage, FileStorage

# Nowe API moduły
try:
    from .api import GameManager, ConfigManager
    __all__ = [
        'HexEngine', 'Player', 'GameState',
        'BasePlayer', 'HumanPlayer', 'ComputerPlayer',
        'ConsoleUI',
        'GameStorage', 'MemoryStorage', 'FileStorage',
        'GameManager', 'ConfigManager'
    ]
except ImportError:
    # Flask dependencies nie są zainstalowane
    __all__ = [
        'HexEngine', 'Player', 'GameState',
        'BasePlayer', 'HumanPlayer', 'ComputerPlayer',
        'ConsoleUI',
        'GameStorage', 'MemoryStorage', 'FileStorage'
    ]