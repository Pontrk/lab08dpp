"""
Silnik gry HEX - niezależny od interfejsu użytkownika
"""

from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import json


class Player(Enum):
    """Enum reprezentujący graczy"""
    NONE = 0
    PLAYER1 = 1  # Gracz 1 (góra-dół)
    PLAYER2 = 2  # Gracz 2 (lewo-prawo)


class GameState(Enum):
    """Stan gry"""
    IN_PROGRESS = "in_progress"
    PLAYER1_WON = "player1_won"
    PLAYER2_WON = "player2_won"
    DRAW = "draw"


class HexEngine:
    """
    Silnik gry HEX - zawiera całą logikę gry, niezależny od interfejsu
    """
    
    def __init__(self, board_size: int = 11):
        """
        Inicjalizuje nową grę HEX
        
        Args:
            board_size: Rozmiar planszy (domyślnie 11x11)
        """
        if board_size < 3:
            raise ValueError("Rozmiar planszy musi być co najmniej 3")
        
        self.board_size = board_size
        self.board = [[Player.NONE for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = Player.PLAYER1
        self.moves = []  # Historia ruchów: [(row, col, player), ...]
        self.game_state = GameState.IN_PROGRESS
        self.winner = None
        
    def get_board_state(self) -> List[List[int]]:
        """
        Zwraca aktualny stan planszy jako listę list intów
        
        Returns:
            Plansza gdzie 0=puste pole, 1=gracz1, 2=gracz2
        """
        return [[cell.value for cell in row] for row in self.board]
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """
        Sprawdza czy ruch jest prawidłowy
        
        Args:
            row, col: Współrzędne ruchu
            
        Returns:
            True jeśli ruch jest prawidłowy
        """
        if self.game_state != GameState.IN_PROGRESS:
            return False
            
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
            
        return self.board[row][col] == Player.NONE
    
    def make_move(self, row: int, col: int) -> bool:
        """
        Wykonuje ruch
        
        Args:
            row, col: Współrzędne ruchu
            
        Returns:
            True jeśli ruch został wykonany, False w przeciwnym razie
        """
        if not self.is_valid_move(row, col):
            return False
        
        # Wykonaj ruch
        self.board[row][col] = self.current_player
        self.moves.append((row, col, self.current_player.value))
        
        # Sprawdź czy gra się skończyła
        if self._check_win(self.current_player):
            self.game_state = GameState.PLAYER1_WON if self.current_player == Player.PLAYER1 else GameState.PLAYER2_WON
            self.winner = self.current_player.value
        elif self._is_board_full():
            self.game_state = GameState.DRAW
        
        # Zmień gracza
        if self.game_state == GameState.IN_PROGRESS:
            self.current_player = Player.PLAYER2 if self.current_player == Player.PLAYER1 else Player.PLAYER1
        
        return True
    
    def _check_win(self, player: Player) -> bool:
        """
        Sprawdza czy dany gracz wygrał
        
        Args:
            player: Gracz do sprawdzenia
            
        Returns:
            True jeśli gracz wygrał
        """
        if player == Player.PLAYER1:
            # Gracz 1 wygrywa łącząc górę z dołem
            return self._has_path_top_to_bottom(player)
        else:
            # Gracz 2 wygrywa łącząc lewo z prawem
            return self._has_path_left_to_right(player)
    
    def _has_path_top_to_bottom(self, player: Player) -> bool:
        """Sprawdza czy istnieje ścieżka od góry do dołu dla gracza"""
        visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        # Rozpocznij od górnego rzędu
        for col in range(self.board_size):
            if self.board[0][col] == player:
                if self._dfs_vertical(0, col, player, visited):
                    return True
        return False
    
    def _has_path_left_to_right(self, player: Player) -> bool:
        """Sprawdza czy istnieje ścieżka od lewej do prawej dla gracza"""
        visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        # Rozpocznij od lewej kolumny
        for row in range(self.board_size):
            if self.board[row][0] == player:
                if self._dfs_horizontal(row, 0, player, visited):
                    return True
        return False
    
    def _dfs_vertical(self, row: int, col: int, player: Player, visited: List[List[bool]]) -> bool:
        """DFS dla ścieżki pionowej (góra-dół)"""
        if row == self.board_size - 1:  # Dotarliśmy do dołu
            return True
        
        visited[row][col] = True
        
        # Sprawdź wszystkich sąsiadów hex
        for dr, dc in self._get_hex_neighbors():
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.board_size and 
                0 <= new_col < self.board_size and
                not visited[new_row][new_col] and
                self.board[new_row][new_col] == player):
                
                if self._dfs_vertical(new_row, new_col, player, visited):
                    return True
        
        return False
    
    def _dfs_horizontal(self, row: int, col: int, player: Player, visited: List[List[bool]]) -> bool:
        """DFS dla ścieżki poziomej (lewo-prawo)"""
        if col == self.board_size - 1:  # Dotarliśmy do prawej
            return True
        
        visited[row][col] = True
        
        # Sprawdź wszystkich sąsiadów hex
        for dr, dc in self._get_hex_neighbors():
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.board_size and 
                0 <= new_col < self.board_size and
                not visited[new_row][new_col] and
                self.board[new_row][new_col] == player):
                
                if self._dfs_horizontal(new_row, new_col, player, visited):
                    return True
        
        return False
    
    def _get_hex_neighbors(self) -> List[Tuple[int, int]]:
        """
        Zwraca listę przesunięć dla sąsiadów w siatce hex
        
        Returns:
            Lista krotek (delta_row, delta_col) dla 6 kierunków
        """
        return [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
    
    def _is_board_full(self) -> bool:
        """Sprawdza czy plansza jest pełna"""
        for row in self.board:
            for cell in row:
                if cell == Player.NONE:
                    return False
        return True
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """
        Zwraca listę pustych pól
        
        Returns:
            Lista krotek (row, col) z pustymi polami
        """
        empty_cells = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == Player.NONE:
                    empty_cells.append((row, col))
        return empty_cells
    
    def get_game_info(self) -> Dict[str, Any]:
        """
        Zwraca informacje o stanie gry
        
        Returns:
            Słownik z informacjami o grze
        """
        return {
            'board_size': self.board_size,
            'current_player': self.current_player.value,
            'game_state': self.game_state.value,
            'winner': self.winner,
            'moves_count': len(self.moves),
            'empty_cells_count': len(self.get_empty_cells())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializuje stan gry do słownika (gotowe dla JSON)
        
        Returns:
            Słownik reprezentujący stan gry
        """
        return {
            'board_size': self.board_size,
            'board': self.get_board_state(),
            'current_player': self.current_player.value,
            'moves': self.moves.copy(),
            'game_state': self.game_state.value,
            'winner': self.winner
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Wczytuje stan gry ze słownika
        
        Args:
            data: Słownik ze stanem gry
        """
        self.board_size = data['board_size']
        self.current_player = Player(data['current_player'])
        self.moves = data['moves'].copy()
        self.game_state = GameState(data['game_state'])
        self.winner = data['winner']
        
        # Odtwórz planszę na podstawie ruchów
        self.board = [[Player.NONE for _ in range(self.board_size)] for _ in range(self.board_size)]
        for row, col, player_value in self.moves:
            self.board[row][col] = Player(player_value)
    
    def save_to_file(self, filename: str) -> None:
        """
        Zapisuje stan gry do pliku JSON
        
        Args:
            filename: Nazwa pliku
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filename: str) -> None:
        """
        Wczytuje stan gry z pliku JSON
        
        Args:
            filename: Nazwa pliku
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.from_dict(data)