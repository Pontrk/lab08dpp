"""
Config Manager - Zarządzanie konfiguracją aplikacji Flask
"""

import os
import json
from typing import Dict, Any


class Config:
    """Bazowa konfiguracja"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hex-game-secret-key-2025'
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE') or 'memory'
    STORAGE_DIR = os.environ.get('STORAGE_DIR') or 'saved_games'
    MAX_GAMES = int(os.environ.get('MAX_GAMES', 100))
    MAX_BOARD_SIZE = int(os.environ.get('MAX_BOARD_SIZE', 25))
    MIN_BOARD_SIZE = int(os.environ.get('MIN_BOARD_SIZE', 3))
    
    # Timeouts
    GAME_TIMEOUT_MINUTES = int(os.environ.get('GAME_TIMEOUT_MINUTES', 60))
    MOVE_TIMEOUT_SECONDS = int(os.environ.get('MOVE_TIMEOUT_SECONDS', 30))
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    
    # CORS
    CORS_ENABLED = os.environ.get('CORS_ENABLED', 'true').lower() == 'true'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Konfiguracja dla developmentu"""
    DEBUG = True
    TESTING = False
    STORAGE_TYPE = 'memory'
    MAX_GAMES = 50
    RATE_LIMIT_ENABLED = False


class ProductionConfig(Config):
    """Konfiguracja dla produkcji"""
    DEBUG = False
    TESTING = False
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'file')
    MAX_GAMES = int(os.environ.get('MAX_GAMES', 1000))
    RATE_LIMIT_ENABLED = True


class TestingConfig(Config):
    """Konfiguracja dla testów"""
    DEBUG = True
    TESTING = True
    STORAGE_TYPE = 'memory'
    MAX_GAMES = 10
    RATE_LIMIT_ENABLED = False


class ConfigManager:
    """Manager konfiguracji"""
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    def __init__(self):
        self.config_file_path = 'config/flask_config.json'
        self.custom_config = self._load_config_file()
    
    def get_config(self, config_name: str = 'development') -> Dict[str, Any]:
        """
        Pobiera konfigurację dla danego środowiska
        
        Args:
            config_name: Nazwa środowiska (development/production/testing)
            
        Returns:
            Słownik z konfiguracją
        """
        if config_name not in self.configs:
            config_name = 'development'
        
        config_class = self.configs[config_name]
        config_dict = {}
        
        # Pobierz wszystkie atrybuty z klasy konfiguracji
        for attr in dir(config_class):
            if not attr.startswith('_'):
                config_dict[attr] = getattr(config_class, attr)
        
        # Walidacja SECRET_KEY dla production
        if config_name == 'production' and not os.environ.get('SECRET_KEY'):
            print("⚠️  Ostrzeżenie: SECRET_KEY nie jest ustawiony dla produkcji!")
            print("   Używam domyślnego klucza deweloperskiego.")
            config_dict['SECRET_KEY'] = 'dev-secret-key-hex-game-2025'
        
        # Nadpisz z pliku konfiguracji jeśli istnieje
        if self.custom_config:
            config_dict.update(self.custom_config.get(config_name, {}))
        
        return config_dict
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Wczytuje konfigurację z pliku JSON"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ostrzeżenie: Nie udało się wczytać pliku konfiguracji: {e}")
        
        return {}
    
    def save_config_file(self, config: Dict[str, Any], config_name: str = 'development') -> bool:
        """Zapisuje konfigurację do pliku"""
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            
            # Wczytaj istniejącą konfigurację
            full_config = self.custom_config or {}
            full_config[config_name] = config
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            
            self.custom_config = full_config
            return True
            
        except Exception as e:
            print(f"Błąd zapisywania konfiguracji: {e}")
            return False
    
    def get_available_configs(self) -> list:
        """Zwraca listę dostępnych konfiguracji"""
        return list(self.configs.keys())
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Waliduje konfigurację
        
        Returns:
            Słownik z błędami walidacji (pusty jeśli OK)
        """
        errors = {}
        
        # Walidacja STORAGE_TYPE
        if 'STORAGE_TYPE' in config:
            if config['STORAGE_TYPE'] not in ['memory', 'file']:
                errors['STORAGE_TYPE'] = 'Musi być "memory" lub "file"'
        
        # Walidacja MAX_GAMES
        if 'MAX_GAMES' in config:
            try:
                max_games = int(config['MAX_GAMES'])
                if max_games < 1 or max_games > 10000:
                    errors['MAX_GAMES'] = 'Musi być między 1 a 10000'
            except (ValueError, TypeError):
                errors['MAX_GAMES'] = 'Musi być liczbą całkowitą'
        
        # Walidacja MAX_BOARD_SIZE
        if 'MAX_BOARD_SIZE' in config:
            try:
                max_size = int(config['MAX_BOARD_SIZE'])
                if max_size < 3 or max_size > 50:
                    errors['MAX_BOARD_SIZE'] = 'Musi być między 3 a 50'
            except (ValueError, TypeError):
                errors['MAX_BOARD_SIZE'] = 'Musi być liczbą całkowitą'
        
        # Walidacja MIN_BOARD_SIZE
        if 'MIN_BOARD_SIZE' in config:
            try:
                min_size = int(config['MIN_BOARD_SIZE'])
                if min_size < 3:
                    errors['MIN_BOARD_SIZE'] = 'Musi być co najmniej 3'
            except (ValueError, TypeError):
                errors['MIN_BOARD_SIZE'] = 'Musi być liczbą całkowitą'
        
        # Sprawdź czy MIN <= MAX
        if 'MIN_BOARD_SIZE' in config and 'MAX_BOARD_SIZE' in config:
            try:
                if int(config['MIN_BOARD_SIZE']) > int(config['MAX_BOARD_SIZE']):
                    errors['BOARD_SIZE'] = 'MIN_BOARD_SIZE nie może być większy niż MAX_BOARD_SIZE'
            except (ValueError, TypeError):
                pass  # Błędy już złapane wyżej
        
        return errors


# Przykładowy plik konfiguracji JSON
EXAMPLE_CONFIG = {
    "development": {
        "DEBUG": True,
        "STORAGE_TYPE": "memory",
        "MAX_GAMES": 50,
        "RATE_LIMIT_ENABLED": False
    },
    "production": {
        "DEBUG": False,
        "STORAGE_TYPE": "file",
        "STORAGE_DIR": "/var/lib/hex-game/saves",
        "MAX_GAMES": 1000,
        "RATE_LIMIT_ENABLED": True,
        "RATE_LIMIT_PER_MINUTE": 120
    },
    "testing": {
        "DEBUG": True,
        "TESTING": True,
        "STORAGE_TYPE": "memory",
        "MAX_GAMES": 10
    }
}


def create_example_config_file():
    """Tworzy przykładowy plik konfiguracji"""
    config_dir = 'config'
    config_file = os.path.join(config_dir, 'flask_config.json')
    
    if not os.path.exists(config_file):
        os.makedirs(config_dir, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(EXAMPLE_CONFIG, f, indent=2, ensure_ascii=False)
        
        print(f"Utworzono przykładowy plik konfiguracji: {config_file}")
    else:
        print(f"Plik konfiguracji już istnieje: {config_file}")


if __name__ == '__main__':
    # Tworzenie przykładowego pliku konfiguracji
    create_example_config_file()
    
    # Test managera konfiguracji
    manager = ConfigManager()
    
    print("Dostępne konfiguracje:", manager.get_available_configs())
    print("\nKonfiguracja development:")
    for key, value in manager.get_config('development').items():
        print(f"  {key}: {value}")