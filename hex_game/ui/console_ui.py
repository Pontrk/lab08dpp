"""
Konsolowy interfejs użytkownika dla gry HEX
"""

from typing import List
from ..core.engine import HexEngine, Player, GameState
from ..players.base_player import BasePlayer


class ConsoleUI:
    """Konsolowy interfejs użytkownika"""
    
    def __init__(self):
        """Inicjalizuje interfejs"""
        self.player_symbols = {
            Player.NONE: '·',
            Player.PLAYER1: '●',  # Gracz 1
            Player.PLAYER2: '○'   # Gracz 2
        }
    
    def display_board(self, engine: HexEngine) -> None:
        """
        Wyświetla planszę gry w klasycznym stylu HEX (romb)
        
        Args:
            engine: Silnik gry
        """
        board = engine.get_board_state()
        size = engine.board_size
        
        print()
        
        # Górna krawędź z numerami kolumn
        print("    ", end="")
        for col in range(size):
            print(f"{col+1:2}", end=" ")
        print()
        
        # Górna krawędź planszy
        print("   ╭" + "─" * (size * 3 - 1) + "╮")
        
        # Wiersze planszy
        for row in range(size):
            # Numer wiersza
            print(f"{row+1:2} ", end="")
            
            # Wcięcie dla kształtu hex
            print(" " * row, end="")
            
            # Lewy brzeg
            if row == 0:
                print("│", end="")
            else:
                print("╲", end="")
            
            # Pola w wierszu
            for col in range(size):
                cell_value = Player(board[row][col])
                symbol = self.player_symbols[cell_value]
                
                print(f" {symbol}", end="")
                if col < size - 1:
                    print(" ", end="")
            
            # Prawy brzeg
            if row == size - 1:
                print(" │", end="")
            else:
                print(" ╲", end="")
                
            print()  # Nowa linia
        
        # Dolna krawędź planszy
        print("   " + " " * size + "╰" + "─" * (size * 3 - 1) + "╯")
        
        # Legenda
        print(f"\n   Gracz 1 ({self.player_symbols[Player.PLAYER1]}): łączy górę z dołem")
        print(f"   Gracz 2 ({self.player_symbols[Player.PLAYER2]}): łączy lewą z prawą")
        print()
    
    def display_game_info(self, engine: HexEngine, current_player: BasePlayer) -> None:
        """
        Wyświetla informacje o grze
        
        Args:
            engine: Silnik gry
            current_player: Aktualny gracz
        """
        info = engine.get_game_info()
        
        print(f"Ruch nr {info['moves_count'] + 1}")
        print(f"Kolej gracza: {current_player.name} ({self.player_symbols[Player(info['current_player'])]})")
        print(f"Wolnych pól: {info['empty_cells_count']}")
        print()
    
    def display_winner(self, engine: HexEngine, players: List[BasePlayer]) -> None:
        """
        Wyświetla wynik gry
        
        Args:
            engine: Silnik gry
            players: Lista graczy
        """
        info = engine.get_game_info()
        
        print("\n" + "="*50)
        print("           KONIEC GRY")
        print("="*50)
        
        if info['game_state'] == GameState.DRAW.value:
            print("Remis!")
        elif info['winner']:
            winner = players[info['winner'] - 1]
            winner_symbol = self.player_symbols[Player(info['winner'])]
            print(f"Zwycięzca: {winner.name} ({winner_symbol})")
        
        print(f"Liczba ruchów: {info['moves_count']}")
        print("="*50)
    
    def display_rules(self) -> None:
        """Wyświetla zasady gry"""
        print("\n" + "="*60)
        print("                    ZASADY GRY HEX")
        print("="*60)
        print("1. Gra odbywa się na sześciokątnej planszy.")
        print("2. Dwóch graczy naprzemiennie umieszcza swoje pionki.")
        print(f"3. Gracz 1 ({self.player_symbols[Player.PLAYER1]}) próbuje połączyć górną i dolną krawędź.")
        print(f"4. Gracz 2 ({self.player_symbols[Player.PLAYER2]}) próbuje połączyć lewą i prawą krawędź.")
        print("5. Pierwszy gracz, który utworzy nieprzerwany łańcuch, wygrywa.")
        print("6. Ruchy podaje się jako: numer_wiersza numer_kolumny")
        print("   (numeracja zaczyna się od 1)")
        print("="*60)
    
    def display_help(self) -> None:
        """Wyświetla pomoc"""
        print("\n" + "="*60)
        print("                       POMOC")
        print("="*60)
        print("Komendy dostępne podczas gry:")
        print("• [wiersz] [kolumna] - wykonaj ruch")
        print("• help - wyświetl tę pomoc")
        print("• rules - wyświetl zasady")
        print("• quit - zakończ grę")
        print()
        print("Przykład ruchu: 5 7")
        print("Umieści pionek w wierszu 5, kolumnie 7")
        print("="*60)