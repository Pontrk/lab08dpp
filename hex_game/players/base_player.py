"""
Bazowa klasa gracza
"""

from abc import ABC, abstractmethod
from typing import Tuple
from ..core.engine import HexEngine


class BasePlayer(ABC):
    """Abstrakcyjna klasa gracza"""
    
    def __init__(self, name: str):
        """
        Inicjalizuje gracza
        
        Args:
            name: Nazwa gracza
        """
        self.name = name
    
    @abstractmethod
    def get_move(self, engine: HexEngine) -> Tuple[int, int]:
        """
        Zwraca ruch gracza
        
        Args:
            engine: Silnik gry
            
        Returns:
            Krotka (row, col) z ruchem
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"