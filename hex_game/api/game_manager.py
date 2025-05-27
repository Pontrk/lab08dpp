"""
Game Manager - Zarządza grami w aplikacji Flask
"""

import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from ..core.engine import HexEngine, GameState, Player
from ..players.computer_player import ComputerPlayer
from ..storage.game_storage import GameStorage


class GameSession:
    """Sesja gry z dodatkowymi metadanymi"""
    
    def __init__(self, game_id: str, engine: HexEngine, player1_data: Dict, player2_data: Dict):
        self.game_id = game_id
        self.engine = engine
        self.player1_data = player1_data
        self.player2_data = player2_data
        self.created_at = datetime.now()
        self.last_move_at = datetime.now()
        self.move_times: List[float] = []  # Czasy wykonania ruchów
        self.total_moves = 0
        
        # Tworzenie AI graczy jeśli potrzeba
        self.computer_players = {}
        if player1_data.get('type') == 'computer':
            difficulty = player1_data.get('difficulty', 'medium')
            self.computer_players[1] = ComputerPlayer(player1_data['name'], difficulty)
        
        if player2_data.get('type') == 'computer':
            difficulty = player2_data.get('difficulty', 'medium')
            self.computer_players[2] = ComputerPlayer(player2_data['name'], difficulty)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje sesję do słownika"""
        return {
            'game_id': self.game_id,
            'engine_state': self.engine.to_dict(),
            'player1': self.player1_data,
            'player2': self.player2_data,
            'created_at': self.created_at.isoformat(),
            'last_move_at': self.last_move_at.isoformat(),
            'total_moves': self.total_moves,
            'move_times': self.move_times
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        """Tworzy sesję ze słownika"""
        engine = HexEngine()
        engine.from_dict(data['engine_state'])
        
        session = cls(
            data['game_id'],
            engine,
            data['player1'],
            data['player2']
        )
        
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_move_at = datetime.fromisoformat(data['last_move_at'])
        session.total_moves = data.get('total_moves', 0)
        session.move_times = data.get('move_times', [])
        
        return session


class GameManager:
    """Zarządza wszystkimi grami w aplikacji"""
    
    def __init__(self, storage: GameStorage):
        self.storage = storage
        self.active_sessions: Dict[str, GameSession] = {}
        self.max_games = 100  # Limit gier w pamięci
    
    def create_game(self, board_size: int, player1_data: Dict, player2_data: Dict) -> str:
        """
        Tworzy nową grę
        
        Args:
            board_size: Rozmiar planszy
            player1_data: Dane pierwszego gracza
            player2_data: Dane drugiego gracza
            
        Returns:
            ID utworzonej gry
        """
        # Sprawdzenie limitu gier
        if len(self.active_sessions) >= self.max_games:
            # Usuń najstarszą grę
            oldest_id = min(self.active_sessions.keys(), 
                          key=lambda x: self.active_sessions[x].created_at)
            del self.active_sessions[oldest_id]
        
        # Generowanie unikalnego ID
        game_id = str(uuid.uuid4())
        
        # Tworzenie silnika gry
        engine = HexEngine(board_size)
        
        # Tworzenie sesji
        session = GameSession(game_id, engine, player1_data, player2_data)
        
        # Zapisanie w pamięci i storage
        self.active_sessions[game_id] = session
        self.storage.save_game(game_id, engine)
        
        return game_id
    
    def get_game_state(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera pełny stan gry"""
        session = self._get_session(game_id)
        if not session:
            return None
        
        engine_info = session.engine.get_game_info()
        
        return {
            'game_id': game_id,
            'board_size': session.engine.board_size,
            'board': session.engine.get_board_state(),
            'current_player': engine_info['current_player'],
            'game_state': engine_info['game_state'],
            'winner': engine_info['winner'],
            'moves_count': engine_info['moves_count'],
            'empty_cells_count': engine_info['empty_cells_count'],
            'player1': session.player1_data,
            'player2': session.player2_data,
            'created_at': session.created_at.isoformat(),
            'last_move_at': session.last_move_at.isoformat(),
            'is_finished': engine_info['game_state'] != GameState.IN_PROGRESS.value
        }
    
    def make_move(self, game_id: str, row: int, col: int) -> Dict[str, Any]:
        """
        Wykonuje ruch w grze
        
        Args:
            game_id: ID gry
            row: Wiersz (0-indexed)
            col: Kolumna (0-indexed)
            
        Returns:
            Wynik ruchu
        """
        session = self._get_session(game_id)
        if not session:
            return {'error': 'Gra nie została znaleziona'}
        
        engine = session.engine
        
        # Sprawdzenie czy gra jest w toku
        if engine.game_state != GameState.IN_PROGRESS:
            return {'error': 'Gra została już zakończona'}
        
        # Sprawdzenie poprawności ruchu
        if not engine.is_valid_move(row, col):
            return {'error': 'Nieprawidłowy ruch'}
        
        # Wykonanie ruchu z pomiarem czasu
        start_time = time.time()
        success = engine.make_move(row, col)
        move_time = time.time() - start_time
        
        if not success:
            return {'error': 'Nie udało się wykonać ruchu'}
        
        # Aktualizacja statystyk sesji
        session.last_move_at = datetime.now()
        session.total_moves += 1
        session.move_times.append(move_time)
        
        # Zapisanie w storage
        self.storage.save_game(game_id, engine)
        
        # Przygotowanie odpowiedzi
        result = {
            'success': True,
            'move': {'row': row, 'col': col, 'player': engine.current_player.value},
            'game_state': self.get_game_state(game_id),
            'move_time': move_time
        }
        
        # Sprawdzenie czy gra się skończyła
        if engine.game_state != GameState.IN_PROGRESS:
            result['game_finished'] = True
            result['winner'] = engine.winner
        
        return result
    
    def make_computer_move(self, game_id: str) -> Dict[str, Any]:
        """Wykonuje automatyczny ruch komputera"""
        session = self._get_session(game_id)
        if not session:
            return {'error': 'Gra nie została znaleziona'}
        
        engine = session.engine
        current_player_num = engine.current_player.value
        
        # Sprawdzenie czy aktualny gracz to komputer
        if current_player_num not in session.computer_players:
            return {'error': f'Gracz {current_player_num} nie jest komputerem'}
        
        # Sprawdzenie czy gra jest w toku
        if engine.game_state != GameState.IN_PROGRESS:
            return {'error': 'Gra została już zakończona'}
        
        # Pobranie ruchu od AI
        computer_player = session.computer_players[current_player_num]
        
        try:
            start_time = time.time()
            row, col = computer_player.get_move(engine)
            move_time = time.time() - start_time
            
            # Wykonanie ruchu
            return self.make_move(game_id, row, col)
            
        except Exception as e:
            return {'error': f'Błąd AI: {str(e)}'}
    
    def get_board_visualization(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera wizualizację planszy"""
        session = self._get_session(game_id)
        if not session:
            return None
        
        engine = session.engine
        board = engine.get_board_state()
        
        # Konwersja do czytelnego formatu
        board_display = []
        for row in board:
            row_display = []
            for cell in row:
                if cell == 0:
                    row_display.append('·')
                elif cell == 1:
                    row_display.append('●')
                else:
                    row_display.append('○')
            board_display.append(row_display)
        
        return {
            'game_id': game_id,
            'board_size': engine.board_size,
            'board_raw': board,
            'board_display': board_display,
            'current_player': engine.current_player.value,
            'game_state': engine.game_state.value,
            'empty_cells': engine.get_empty_cells()
        }
    
    def list_games(self) -> List[Dict[str, Any]]:
        """Lista wszystkich aktywnych gier"""
        games = []
        
        for game_id, session in self.active_sessions.items():
            engine_info = session.engine.get_game_info()
            games.append({
                'game_id': game_id,
                'board_size': session.engine.board_size,
                'game_state': engine_info['game_state'],
                'moves_count': engine_info['moves_count'],
                'current_player': engine_info['current_player'],
                'player1': session.player1_data,
                'player2': session.player2_data,
                'created_at': session.created_at.isoformat(),
                'last_move_at': session.last_move_at.isoformat()
            })
        
        return sorted(games, key=lambda x: x['created_at'], reverse=True)
    
    def delete_game(self, game_id: str) -> bool:
        """Usuwa grę"""
        if game_id in self.active_sessions:
            del self.active_sessions[game_id]
            self.storage.delete_game(game_id)
            return True
        return False
    
    def save_game_to_file(self, game_id: str, filename: str) -> bool:
        """Zapisuje grę do pliku"""
        session = self._get_session(game_id)
        if not session:
            return False
        
        try:
            session.engine.save_to_file(filename)
            return True
        except Exception:
            return False
    
    def load_game_from_file(self, filename: str) -> Optional[str]:
        """Wczytuje grę z pliku"""
        try:
            # Tworzenie nowego silnika i wczytanie
            engine = HexEngine()
            engine.load_from_file(filename)
            
            # Generowanie nowego ID
            game_id = str(uuid.uuid4())
            
            # Tworzenie sesji z domyślnymi danymi graczy
            player1_data = {'type': 'human', 'name': 'Gracz 1'}
            player2_data = {'type': 'human', 'name': 'Gracz 2'}
            
            session = GameSession(game_id, engine, player1_data, player2_data)
            
            # Zapisanie
            self.active_sessions[game_id] = session
            self.storage.save_game(game_id, engine)
            
            return game_id
            
        except Exception:
            return None
    
    def get_game_statistics(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera statystyki konkretnej gry"""
        session = self._get_session(game_id)
        if not session:
            return None
        
        move_times = session.move_times
        
        return {
            'game_id': game_id,
            'total_moves': session.total_moves,
            'average_move_time': sum(move_times) / len(move_times) if move_times else 0,
            'fastest_move': min(move_times) if move_times else 0,
            'slowest_move': max(move_times) if move_times else 0,
            'total_game_time': (session.last_move_at - session.created_at).total_seconds(),
            'moves_per_minute': session.total_moves / max(1, (session.last_move_at - session.created_at).total_seconds() / 60)
        }
    
    def get_global_statistics(self) -> Dict[str, Any]:
        """Pobiera globalne statystyki"""
        total_games = len(self.active_sessions)
        finished_games = sum(1 for s in self.active_sessions.values() 
                           if s.engine.game_state != GameState.IN_PROGRESS)
        
        all_move_times = []
        total_moves = 0
        
        for session in self.active_sessions.values():
            all_move_times.extend(session.move_times)
            total_moves += session.total_moves
        
        return {
            'total_games': total_games,
            'active_games': total_games - finished_games,
            'finished_games': finished_games,
            'total_moves': total_moves,
            'average_move_time': sum(all_move_times) / len(all_move_times) if all_move_times else 0,
            'storage_type': type(self.storage).__name__
        }
    
    def _get_session(self, game_id: str) -> Optional[GameSession]:
        """Pobiera sesję gry (najpierw z pamięci, potem ze storage)"""
        # Sprawdź pamięć
        if game_id in self.active_sessions:
            return self.active_sessions[game_id]
        
        # Spróbuj wczytać ze storage
        engine = self.storage.load_game(game_id)
        if engine:
            # Tworzenie sesji z domyślnymi danymi graczy
            player1_data = {'type': 'human', 'name': 'Gracz 1'}
            player2_data = {'type': 'human', 'name': 'Gracz 2'}
            
            session = GameSession(game_id, engine, player1_data, player2_data)
            self.active_sessions[game_id] = session
            return session
        
        return None