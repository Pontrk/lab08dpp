"""
Abstrakcyjne klasy dla przechowywania gier - przygotowanie na Flask
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
import json
import os
from datetime import datetime
from ..core.engine import HexEngine


class GameStorage(ABC):
    """Abstrakcyjna klasa dla przechowywania gier"""
    
    @abstractmethod
    def save_game(self, game_id: str, engine: HexEngine) -> bool:
        """Zapisuje grę"""
        pass
    
    @abstractmethod
    def load_game(self, game_id: str) -> Optional[HexEngine]:
        """Wczytuje grę"""
        pass
    
    @abstractmethod
    def delete_game(self, game_id: str) -> bool:
        """Usuwa grę"""
        pass
    
    @abstractmethod
    def list_games(self) -> List[str]:
        """Zwraca listę dostępnych gier"""
        pass


class MemoryStorage(GameStorage):
    """Przechowywanie gier w pamięci - szybkie, ale nietrwałe"""
    
    def __init__(self):
        self._games: Dict[str, Dict] = {}
    
    def save_game(self, game_id: str, engine: HexEngine) -> bool:
        """Zapisuje grę w pamięci"""
        try:
            self._games[game_id] = {
                'data': engine.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            return True
        except Exception:
            return False
    
    def load_game(self, game_id: str) -> Optional[HexEngine]:
        """Wczytuje grę z pamięci"""
        if game_id not in self._games:
            return None
        
        try:
            engine = HexEngine()
            engine.from_dict(self._games[game_id]['data'])
            return engine
        except Exception:
            return None
    
    def delete_game(self, game_id: str) -> bool:
        """Usuwa grę z pamięci"""
        if game_id in self._games:
            del self._games[game_id]
            return True
        return False
    
    def list_games(self) -> List[str]:
        """Zwraca listę gier w pamięci"""
        return list(self._games.keys())


class FileStorage(GameStorage):
    """Przechowywanie gier w plikach - trwałe, ale wolniejsze"""
    
    def __init__(self, storage_dir: str = "saved_games"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_file_path(self, game_id: str) -> str:
        """Zwraca ścieżkę do pliku gry"""
        return os.path.join(self.storage_dir, f"{game_id}.json")
    
    def save_game(self, game_id: str, engine: HexEngine) -> bool:
        """Zapisuje grę do pliku"""
        try:
            data = {
                'game_data': engine.to_dict(),
                'timestamp': datetime.now().isoformat(),
                'game_id': game_id
            }
            
            with open(self._get_file_path(game_id), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_game(self, game_id: str) -> Optional[HexEngine]:
        """Wczytuje grę z pliku"""
        file_path = self._get_file_path(game_id)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            engine = HexEngine()
            engine.from_dict(data['game_data'])
            return engine
        except Exception:
            return None
    
    def delete_game(self, game_id: str) -> bool:
        """Usuwa plik gry"""
        file_path = self._get_file_path(game_id)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
    
    def list_games(self) -> List[str]:
        """Zwraca listę zapisanych gier"""
        try:
            files = os.listdir(self.storage_dir)
            return [f[:-5] for f in files if f.endswith('.json')]  # Usuwa .json
        except Exception:
            return []