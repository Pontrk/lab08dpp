#!/usr/bin/env python3
"""
Flask API dla gry HEX
"""

from flask import Flask, request, jsonify, render_template
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from hex_game.core.engine import HexEngine, GameState, Player
from hex_game.players.computer_player import ComputerPlayer
from hex_game.storage.game_storage import MemoryStorage, FileStorage
from hex_game.api.game_manager import GameManager
from hex_game.api.config_manager import ConfigManager


def create_app(config_name: str = 'development') -> Flask:
    """Factory do tworzenia aplikacji Flask"""
    
    app = Flask(__name__)
    
    # Konfiguracja aplikacji
    config_manager = ConfigManager()
    app.config.update(config_manager.get_config(config_name))
    
    # Inicjalizacja storage na podstawie konfiguracji
    storage_type = app.config.get('STORAGE_TYPE', 'memory')
    if storage_type == 'file':
        storage = FileStorage(app.config.get('STORAGE_DIR', 'saved_games'))
    else:
        storage = MemoryStorage()
    
    # Inicjalizacja game managera
    game_manager = GameManager(storage)
    
    # Konfiguracja logowania
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # === ROUTES ===
    
    @app.route('/')
    def index():
        """Strona główna z dokumentacją API"""
        return render_template('index.html')
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'storage_type': storage_type
        })
    
    # === GAME MANAGEMENT ===
    
    @app.route('/api/games', methods=['POST'])
    def create_game():
        """
        Tworzy nową grę
        
        Body:
        {
            "board_size": 11,
            "player1": {"type": "human", "name": "Gracz 1"},
            "player2": {"type": "computer", "name": "AI", "difficulty": "medium"}
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Brak danych JSON'}), 400
            
            # Walidacja danych
            board_size = data.get('board_size', 11)
            if board_size < 3 or board_size > 25:
                return jsonify({'error': 'Rozmiar planszy musi być między 3 a 25'}), 400
            
            player1_data = data.get('player1', {'type': 'human', 'name': 'Gracz 1'})
            player2_data = data.get('player2', {'type': 'computer', 'name': 'AI'})
            
            # Tworzenie gry
            game_id = game_manager.create_game(board_size, player1_data, player2_data)
            
            return jsonify({
                'game_id': game_id,
                'message': 'Gra utworzona pomyślnie',
                'game_state': game_manager.get_game_state(game_id)
            }), 201
            
        except Exception as e:
            app.logger.error(f"Błąd tworzenia gry: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/games', methods=['GET'])
    def list_games():
        """Lista wszystkich gier"""
        try:
            games = game_manager.list_games()
            return jsonify({
                'games': games,
                'count': len(games)
            })
        except Exception as e:
            app.logger.error(f"Błąd listowania gier: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/games/<game_id>', methods=['GET'])
    def get_game(game_id: str):
        """Pobiera stan konkretnej gry"""
        try:
            game_state = game_manager.get_game_state(game_id)
            if not game_state:
                return jsonify({'error': 'Gra nie została znaleziona'}), 404
            
            return jsonify(game_state)
            
        except Exception as e:
            app.logger.error(f"Błąd pobierania gry {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/games/<game_id>', methods=['DELETE'])
    def delete_game(game_id: str):
        """Usuwa grę"""
        try:
            success = game_manager.delete_game(game_id)
            if not success:
                return jsonify({'error': 'Gra nie została znaleziona'}), 404
            
            return jsonify({'message': 'Gra usunięta pomyślnie'})
            
        except Exception as e:
            app.logger.error(f"Błąd usuwania gry {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    # === GAMEPLAY ===
    
    @app.route('/api/games/<game_id>/moves', methods=['POST'])
    def make_move(game_id: str):
        """
        Wykonuje ruch w grze
        
        Body:
        {
            "row": 5,
            "col": 7,
            "player": 1  // opcjonalne - do walidacji
        }
        """
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Brak danych JSON'}), 400
            
            row = data.get('row')
            col = data.get('col')
            
            if row is None or col is None:
                return jsonify({'error': 'Wymagane pola: row, col'}), 400
            
            # Wykonanie ruchu
            result = game_manager.make_move(game_id, row, col)
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"Błąd wykonywania ruchu w grze {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/games/<game_id>/moves/computer', methods=['POST'])
    def make_computer_move(game_id: str):
        """Wykonuje automatyczny ruch komputera"""
        try:
            result = game_manager.make_computer_move(game_id)
            
            if 'error' in result:
                return jsonify(result), 400
            
            return jsonify(result)
            
        except Exception as e:
            app.logger.error(f"Błąd ruchu komputera w grze {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/games/<game_id>/board', methods=['GET'])
    def get_board(game_id: str):
        """Pobiera aktualny stan planszy"""
        try:
            board_data = game_manager.get_board_visualization(game_id)
            
            if not board_data:
                return jsonify({'error': 'Gra nie została znaleziona'}), 404
            
            return jsonify(board_data)
            
        except Exception as e:
            app.logger.error(f"Błąd pobierania planszy gry {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    # === GAME STATE MANAGEMENT ===
    
    @app.route('/api/games/<game_id>/save', methods=['POST'])
    def save_game(game_id: str):
        """Zapisuje grę do pliku"""
        try:
            data = request.get_json() or {}
            filename = data.get('filename', f'game_{game_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            success = game_manager.save_game_to_file(game_id, filename)
            
            if not success:
                return jsonify({'error': 'Nie udało się zapisać gry'}), 500
            
            return jsonify({
                'message': 'Gra zapisana pomyślnie',
                'filename': filename
            })
            
        except Exception as e:
            app.logger.error(f"Błąd zapisywania gry {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/games/load', methods=['POST'])
    def load_game():
        """
        Wczytuje grę z pliku
        
        Body:
        {
            "filename": "game_123.json"
        }
        """
        try:
            data = request.get_json()
            if not data or 'filename' not in data:
                return jsonify({'error': 'Wymagane pole: filename'}), 400
            
            filename = data['filename']
            game_id = game_manager.load_game_from_file(filename)
            
            if not game_id:
                return jsonify({'error': 'Nie udało się wczytać gry'}), 500
            
            return jsonify({
                'message': 'Gra wczytana pomyślnie',
                'game_id': game_id,
                'game_state': game_manager.get_game_state(game_id)
            })
            
        except Exception as e:
            app.logger.error(f"Błąd wczytywania gry: {e}")
            return jsonify({'error': str(e)}), 500
    
    # === STATISTICS ===
    
    @app.route('/api/games/<game_id>/stats', methods=['GET'])
    def get_game_stats(game_id: str):
        """Pobiera statystyki gry"""
        try:
            stats = game_manager.get_game_statistics(game_id)
            
            if not stats:
                return jsonify({'error': 'Gra nie została znaleziona'}), 404
            
            return jsonify(stats)
            
        except Exception as e:
            app.logger.error(f"Błąd pobierania statystyk gry {game_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats', methods=['GET'])
    def get_global_stats():
        """Pobiera globalne statystyki"""
        try:
            stats = game_manager.get_global_statistics()
            return jsonify(stats)
            
        except Exception as e:
            app.logger.error(f"Błąd pobierania globalnych statystyk: {e}")
            return jsonify({'error': str(e)}), 500
    
    # === CONFIGURATION ===
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Pobiera aktualną konfigurację"""
        return jsonify({
            'storage_type': storage_type,
            'config_name': config_name,
            'app_config': {
                'DEBUG': app.config.get('DEBUG', False),
                'STORAGE_TYPE': app.config.get('STORAGE_TYPE'),
                'STORAGE_DIR': app.config.get('STORAGE_DIR'),
                'MAX_GAMES': app.config.get('MAX_GAMES', 100)
            }
        })
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """Aktualizuje konfigurację w runtime"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Brak danych JSON'}), 400
            
            # Tutaj można dodać logikę aktualizacji konfiguracji
            # Na razie tylko zwracamy informację
            return jsonify({
                'message': 'Konfiguracja zostanie zaktualizowana w kolejnej wersji',
                'received_config': data
            })
            
        except Exception as e:
            app.logger.error(f"Błąd aktualizacji konfiguracji: {e}")
            return jsonify({'error': str(e)}), 500
    
    # === ERROR HANDLERS ===
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint nie został znaleziony'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Metoda HTTP nie jest dozwolona'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Wewnętrzny błąd serwera'}), 500
    
    return app


def main():
    """Główna funkcja uruchamiająca serwer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Serwer Flask dla gry HEX')
    parser.add_argument('--host', default='127.0.0.1', help='Adres IP serwera')
    parser.add_argument('--port', type=int, default=5000, help='Port serwera')
    parser.add_argument('--debug', action='store_true', help='Tryb debug')
    parser.add_argument('--config', default='development', 
                       choices=['development', 'production', 'testing'],
                       help='Profil konfiguracji')
    parser.add_argument('--storage', default='memory',
                       choices=['memory', 'file'],
                       help='Typ storage')
    
    args = parser.parse_args()
    
    # Ustawienie zmiennych środowiskowych
    os.environ['FLASK_ENV'] = args.config
    os.environ['STORAGE_TYPE'] = args.storage
    
    # Tworzenie aplikacji
    app = create_app(args.config)
    
    print(f"🚀 Uruchamianie serwera HEX Flask...")
    print(f"📍 Adres: http://{args.host}:{args.port}")
    print(f"⚙️  Konfiguracja: {args.config}")
    print(f"💾 Storage: {args.storage}")
    print(f"🔧 Debug: {args.debug}")
    
    # Uruchomienie serwera
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()