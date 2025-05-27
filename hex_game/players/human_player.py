"""
Gracz człowiek - wprowadza ruchy z klawiatury z dodatkowymi komendami
"""

import json
from typing import Tuple
from .base_player import BasePlayer
from ..core.engine import HexEngine
from ..ui.console_ui import ConsoleUI


class HumanPlayer(BasePlayer):
    """Gracz człowiek z dodatkowymi komendami"""
    
    def get_move(self, engine: HexEngine) -> Tuple[int, int]:
        """
        Pobiera ruch od użytkownika z obsługą dodatkowych komend
        
        Args:
            engine: Silnik gry
            
        Returns:
            Krotka (row, col) z ruchem
        """
        while True:
            try:
                move_input = input(f"{self.name}, podaj ruch (wiersz kolumna) lub komendę: ").strip().lower()
                
                if not move_input:
                    continue
                
                # Obsługa specjalnych komend
                if move_input in ['help', 'h', '?']:
                    self._show_help()
                    continue
                elif move_input in ['rules', 'zasady']:
                    self._show_rules()
                    continue
                elif move_input in ['save', 'zapisz']:
                    filename = input("Podaj nazwę pliku (lub Enter dla 'quick_save.json'): ").strip()
                    if not filename:
                        filename = "quick_save.json"
                    if not filename.endswith('.json'):
                        filename += '.json'
                    try:
                        engine.save_to_file(filename)
                        print(f"✅ Gra zapisana do pliku: {filename}")
                    except Exception as e:
                        print(f"❌ Błąd zapisu: {e}")
                    continue
                elif move_input in ['load', 'wczytaj']:
                    print("⚠️  Wczytanie gry zastąpi bieżącą rozgrywkę!")
                    confirm = input("Czy na pewno? (t/n): ").strip().lower()
                    if confirm in ['t', 'tak', 'y', 'yes']:
                        filename = input("Podaj nazwę pliku do wczytania: ").strip()
                        if filename and not filename.endswith('.json'):
                            filename += '.json'
                        try:
                            engine.load_from_file(filename)
                            print(f"✅ Gra wczytana z pliku: {filename}")
                            print("🔄 Plansza została zaktualizowana")
                        except FileNotFoundError:
                            print(f"❌ Nie znaleziono pliku: {filename}")
                        except Exception as e:
                            print(f"❌ Błąd wczytywania: {e}")
                    continue
                elif move_input in ['quit', 'exit', 'q']:
                    save_choice = input("Czy chcesz zapisać grę przed wyjściem? (t/n): ").strip().lower()
                    if save_choice in ['t', 'tak', 'y', 'yes']:
                        filename = input("Nazwa pliku (Enter = 'exit_save.json'): ").strip()
                        if not filename:
                            filename = "exit_save.json"
                        if not filename.endswith('.json'):
                            filename += '.json'
                        try:
                            engine.save_to_file(filename)
                            print(f"✅ Gra zapisana do pliku: {filename}")
                        except Exception as e:
                            print(f"❌ Błąd zapisu: {e}")
                    raise KeyboardInterrupt()
                elif move_input in ['board', 'plansza']:
                    ui = ConsoleUI()
                    ui.display_board(engine)
                    continue
                
                # Próba parsowania ruchu
                parts = move_input.split()
                if len(parts) != 2:
                    print("❌ Podaj dokładnie dwie liczby oddzielone spacją lub użyj komendy:")
                    print("   help, rules, save, load, quit, board")
                    continue
                
                row = int(parts[0]) - 1  # Konwersja z 1-indexowanego na 0-indexowany
                col = int(parts[1]) - 1
                
                if not engine.is_valid_move(row, col):
                    if not (0 <= row < engine.board_size and 0 <= col < engine.board_size):
                        print(f"❌ Współrzędne muszą być w zakresie 1-{engine.board_size}")
                    else:
                        print("❌ To pole jest już zajęte")
                    continue
                
                return (row, col)
                
            except ValueError:
                print("❌ Podaj prawidłowe liczby lub komendę (help)")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"❌ Błąd: {e}")
    
    def _show_help(self):
        """Wyświetla pomoc"""
        print("\n" + "="*50)
        print("                  KOMENDY GRY")
        print("="*50)
        print("🎯 RUCHY:")
        print("  [wiersz] [kolumna] - wykonaj ruch (np. '5 7')")
        print()
        print("📋 KOMENDY:")
        print("  help, h, ?        - ta pomoc")
        print("  rules, zasady     - zasady gry")
        print("  save, zapisz      - zapisz grę do pliku")
        print("  load, wczytaj     - wczytaj grę z pliku")
        print("  quit, exit, q     - wyjdź z gry")
        print("  board, plansza    - odśwież planszę")
        print()
        print("💾 PRZYKŁADY:")
        print("  5 7               - ruch w wierszu 5, kolumnie 7")
        print("  save              - zapisz grę")
        print("  save moja_gra     - zapisz jako 'moja_gra.json'")
        print("  load       - wczytaj zapis")
        print("="*50)
    
    def _show_rules(self):
        """Wyświetla zasady"""
        print("\n" + "="*60)
        print("                    ZASADY GRY HEX")
        print("="*60)
        print("🎯 CEL GRY:")
        print("  • Gracz 1 (●) - połącz górną i dolną krawędź")
        print("  • Gracz 2 (○) - połącz lewą i prawą krawędź")
        print()
        print("📝 ZASADY:")
        print("  1. Gracze naprzemiennie umieszczają pionki")
        print("  2. Każde pole można użyć tylko raz")
        print("  3. Wygrywa pierwszy gracz z nieprzerwanych łańcuchem")
        print("  4. Brak remisów - zawsze ktoś wygrywa!")
        print()
        print("🔗 POŁĄCZENIA:")
        print("  Pionki łączą się przez boki (6 kierunków w hex)")
        print("="*60)