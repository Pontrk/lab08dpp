# hex_game/players/computer_player.py
"""
Gracz komputer - wykonuje ruchy automatycznie
"""

import random
from typing import Tuple, List
from .base_player import BasePlayer
from ..core.engine import HexEngine, Player


class ComputerPlayer(BasePlayer):
    """Gracz komputer z różnymi poziomami trudności"""
    
    def __init__(self, name: str, difficulty: str = "easy"):
        """
        Inicjalizuje gracza komputerowego
        
        Args:
            name: Nazwa gracza
            difficulty: Poziom trudności ('easy', 'medium', 'hard')
        """
        super().__init__(name)
        self.difficulty = difficulty.lower()
        
        if self.difficulty not in ['easy', 'medium', 'hard']:
            raise ValueError("Dostępne poziomy trudności: easy, medium, hard")
    
    def get_move(self, engine: HexEngine) -> Tuple[int, int]:
        """
        Zwraca ruch komputera
        
        Args:
            engine: Silnik gry
            
        Returns:
            Krotka (row, col) z ruchem
        """
        empty_cells = engine.get_empty_cells()
        
        if not empty_cells:
            raise ValueError("Brak dostępnych ruchów")
        
        if self.difficulty == "easy":
            return self._get_random_move(empty_cells)
        elif self.difficulty == "medium":
            return self._get_medium_move(engine, empty_cells)
        else:  # hard
            return self._get_hard_move(engine, empty_cells)
    
    def _get_random_move(self, empty_cells: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Losowy ruch"""
        return random.choice(empty_cells)
    
    def _get_medium_move(self, engine: HexEngine, empty_cells: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Ruch średnio zaawansowany - preferuje środek planszy i blokuje przeciwnika
        """
        # Sprawdź czy można wygrać w tym ruchu
        winning_move = self._find_winning_move(engine, empty_cells)
        if winning_move:
            return winning_move
        
        # Sprawdź czy trzeba zablokować przeciwnika
        blocking_move = self._find_blocking_move(engine, empty_cells)
        if blocking_move:
            return blocking_move
        
        # W przeciwnym razie wybierz ruch bliżej środka
        center = engine.board_size // 2
        empty_cells.sort(key=lambda pos: abs(pos[0] - center) + abs(pos[1] - center))
        
        return empty_cells[0]
    
    def _get_hard_move(self, engine: HexEngine, empty_cells: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Ruch zaawansowany - używa prostej oceny pozycji
        """
        # Sprawdź czy można wygrać
        winning_move = self._find_winning_move(engine, empty_cells)
        if winning_move:
            return winning_move
        
        # Sprawdź czy trzeba zablokować
        blocking_move = self._find_blocking_move(engine, empty_cells)
        if blocking_move:
            return blocking_move
        
        # Oceń wszystkie możliwe ruchy
        best_move = None
        best_score = -float('inf')
        
        for move in empty_cells:
            score = self._evaluate_move(engine, move)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else random.choice(empty_cells)
    
    def _find_winning_move(self, engine: HexEngine, empty_cells: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Znajduje ruch wygrywający jeśli istnieje"""
        current_player = engine.current_player
        
        for move in empty_cells:
            # Symuluj ruch
            engine.board[move[0]][move[1]] = current_player
            
            # Sprawdź czy wygrywa
            if engine._check_win(current_player):
                # Cofnij ruch
                engine.board[move[0]][move[1]] = Player.NONE
                return move
            
            # Cofnij ruch
            engine.board[move[0]][move[1]] = Player.NONE
        
        return None
    
    def _find_blocking_move(self, engine: HexEngine, empty_cells: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Znajduje ruch blokujący przeciwnika"""
        opponent = Player.PLAYER2 if engine.current_player == Player.PLAYER1 else Player.PLAYER1
        
        for move in empty_cells:
            # Symuluj ruch przeciwnika
            engine.board[move[0]][move[1]] = opponent
            
            # Sprawdź czy przeciwnik by wygrał
            would_win = engine._check_win(opponent)
            
            # Cofnij ruch
            engine.board[move[0]][move[1]] = Player.NONE
            
            if would_win:
                return move
        
        return None
    
    def _evaluate_move(self, engine: HexEngine, move: Tuple[int, int]) -> float:
        """
        Ocenia jakość ruchu
        
        Args:
            engine: Silnik gry
            move: Ruch do oceny
            
        Returns:
            Ocena ruchu (wyższa = lepsza)
        """
        row, col = move
        score = 0.0
        
        # Bonus za bliskość do celu
        if engine.current_player == Player.PLAYER1:
            # Gracz 1 chce łączyć góra-dół
            # Bonus za bycie w środkowych kolumnach
            center_col = engine.board_size // 2
            score += 10 - abs(col - center_col)
            
            # Bonus za połączenie z góra lub dołem
            if row == 0 or row == engine.board_size - 1:
                score += 15
        else:
            # Gracz 2 chce łączyć lewo-prawo
            # Bonus za bycie w środkowych rzędach
            center_row = engine.board_size // 2
            score += 10 - abs(row - center_row)
            
            # Bonus za połączenie z lewą lub prawą
            if col == 0 or col == engine.board_size - 1:
                score += 15
        
        # Bonus za sąsiedztwo z własnymi pionami
        current_player = engine.current_player
        neighbors = 0
        for dr, dc in engine._get_hex_neighbors():
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < engine.board_size and 
                0 <= new_col < engine.board_size and
                engine.board[new_row][new_col] == current_player):
                neighbors += 1
        
        score += neighbors * 5
        
        return score