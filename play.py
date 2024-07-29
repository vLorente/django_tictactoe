import logging
import subprocess
import json
from typing import List
from tabulate import tabulate
from simple_term_menu import TerminalMenu
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

# Configurar el logger
logger = logging.getLogger(__name__)

BASE_URL = 'http://localhost:8000/game/api'

class Player:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
    
class Game:
    def __init__(self, data):
        self.id = data['id']
        self.player1 = Player(data['player1'])
        self.player2 = Player(data['player2'])
        self.current_turn = Player(data['current_turn'])
        self.winner = Player(data['winner']) if data['winner'] else None
        self.state = data['state']
        self.board = data['board']

class Move:
    def __init__(self, data):
        self.id = data['id']

class IDValidator(Validator):
    def __init__(self, valid_ids):
        self.valid_ids = valid_ids

    def validate(self, document):
        text = document.text
        if not text.isdigit():
            raise ValidationError(message='El ID debe ser un número.', cursor_position=len(text))
        id = int(text)
        if id not in self.valid_ids:
            raise ValidationError(message='ID no válido o ya seleccionado.', cursor_position=len(text))

def print_error(msg):
    print('\033[91m'+msg+'\033[0m')
def print_warning(msg):
    print('\033[93m'+msg+'\033[0m')
def print_info(msg):
    print('\033[96m'+msg+'\033[0m')
    
def print_board(board):
    print(f"""
    | {board[0]} | {board[1]} | {board[2]} |
    -------------
    | {board[3]} | {board[4]} | {board[5]} |
    -------------
    | {board[6]} | {board[7]} | {board[8]} |
    """)

def print_players(players: List[Player]):
    if not players:
        print('No hay jugadores disponibles.')
        return
    
    table = [[player.id, player.name] for player in players]
    
    print(tabulate(table, headers=['ID', 'Nombre'], tablefmt='grid'))
    
def print_games(games: List[Game]):
    if not games:
        print('No hay jugadores disponibles.')
        return
    
    table = [[game.id, game.player1.name, game.player2.name, game.current_turn.name, game.state] for game in games]
    
    print(tabulate(table, headers=['ID', 'Jugador 1', 'Jugador 2', 'Siguiente Turno', 'Estado'], tablefmt='grid'))

def run_curl_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return json.loads(result.stdout.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        print(f'Error: {e.stderr.decode("utf-8")}')
        return None

def create_player_curl(name):
    command = f"curl -X POST {BASE_URL}/players/ -H 'Content-Type: application/json' -d '{{\"name\": \"{name}\"}}'"
    return run_curl_command(command)

def get_players_curl():
    command = f"curl -X GET {BASE_URL}/players/ -H 'Content-Type: application/json'"
    return run_curl_command(command)

def create_game_curl(player1_id, player2_id):
    command = f"curl -X POST {BASE_URL}/games/ -H 'Content-Type: application/json' -d '{{\"player1\": {player1_id}, \"player2\": {player2_id}}}'"
    return run_curl_command(command)

def get_game_curl(game_id):
    command = f"curl -X GET {BASE_URL}/games/{game_id}/ -H 'Content-Type: application/json'"
    return run_curl_command(command)

def get_games_curl():
    command = f"curl -X GET {BASE_URL}/games/ -H 'Content-Type: application/json'"
    return run_curl_command(command)

def get_in_progress_games_curl():
    command = f"curl -X GET {BASE_URL}/games/?state=progress -H 'Content-Type: application/json'"
    return run_curl_command(command)

def get_finished_games_curl():
    command = f"curl -X GET {BASE_URL}/games/?state=finished -H 'Content-Type: application/json'"
    return run_curl_command(command)

def make_move_curl(game_id, player_id, position):
    command = f"curl -X POST {BASE_URL}/games/{game_id}/make_move/ -H 'Content-Type: application/json' -d '{{\"player\": {player_id}, \"position\": {position}}}'"
    return run_curl_command(command)

def prompt_for_id(prompt_text, valid_ids):
    validator = IDValidator(valid_ids)
    while True:
        try:
            id_str = prompt(prompt_text, validator=validator)
            return int(id_str)
        except ValidationError as e:
            print(e.message)

def create_new_player():
    print_info('\nJugadores existentes')
    players = [Player(player) for player in get_players_curl()]
    print_players(players)
    player_name = input('\nNombre del jugador: ')
    player = create_player_curl(player_name)
    if player and 'name' not in player:
        print(f'Jugador creado con ID: {player["id"]}')
    else:
        detail = player['name']
        print(f'Fallo al crear el jugador: {detail}.')

def create_new_game():
    print_info('Creación de nueva partida')
    players = [Player(player) for player in get_players_curl()]
    valid_ids = [player.id for player in players]
    if players and len(players) < 2:
        print_warning('\n**Deben existir al menos dos jugadores para poder jugar una partida.\n')
        return
    
    print_players(players)
    
    player1_id = prompt_for_id('Seleccione ID Jugador 1: ', valid_ids)
    valid_ids.remove(player1_id)
    player2_id = prompt_for_id('Seleccione ID Jugador 2: ', valid_ids)

    game = create_game_curl(player1_id, player2_id)
    
    if not game:
        print('Fallo al crear la partida.')
        return
    
    print(f'Partida creada con ID: {game["id"]}')
    return game['id']

def continue_game():
    games = [Game(game) for game in get_in_progress_games_curl()]
    if not games:
        print('No hay partidas disponibles.')
        return None

    print('Historial de partidas:')
    print_games(games)
    
    valid_ids = [game.id for game in games]
    game_id = prompt_for_id('Ingrese el ID de la partida que desea continuar: ', valid_ids)
    return game_id
    
def play_game(game_id):
    game = Game(get_game_curl(game_id))
    if not game:
        print('Partida no encontrada.')
        return
    
    while True:
        if game.state == 'finished':
            print_board(game.board)
            if not game.winner:
                print_info("Partida terminada... ¡Es un empate!")
            else:
                print_info(f"!Patida terminada! Gana {game.winner.name}.")
            break
        
        current_turn_id = game.current_turn.id
        current_turn_name = game.current_turn.name
        print_board(game.board)
        print(f'Turno de: {current_turn_name}')
        
        position = int(input(f'Ingrese posición para {current_turn_name} (1-9): ')) -1
        
        logger.error(f'POSITION -> {position}')

        move_response = make_move_curl(game_id, current_turn_id, position)            
        
        if move_response and not 'detail' in move_response:
            game = Game(move_response)
        else:
            print_warning("Movimiento inválido, inténtalo de nuevo.")

    
    
def main():
    print('Bienvenido a Tic-Tac-Toe!')
    menu_options = [
        'Crear jugador',
        'Nueva partida',
        'Continuar partida',
        'Historial de partidas',
        'Salir'
    ]
    menu = TerminalMenu(menu_options)
    menu_history_options = [
                    'Todas las partidas',
                    'Partidas en curso',
                    'Partidas terminadas',
                    'Partidas por jugador',
                    'Volver'
    ]
    history_menu = TerminalMenu(menu_history_options)
    while True:
        
        choice = menu.show()
        
        match choice:
            case 0:
                create_new_player()
            case 1:
                game_id = create_new_game()
                play_game(game_id)
            case 2:
                game_id = continue_game()
                if game_id:
                    play_game(game_id)
            case 3:
                print('\n')
                choice = history_menu.show()
                match choice:
                    case 0:
                        games = [Game(game) for game in get_games_curl()]
                        print_games(games)
                    case 1:
                        games = [Game(game) for game in get_in_progress_games_curl()]
                        print_games(games)
                    case 2:
                        games = [Game(game) for game in get_finished_games_curl()]
                        print_games(games)
                    case 4:
                        print('\n')
                        continue
                    case _:
                        print_warning('Opción no válida. Por favor, intente de nuevo.')

            case 4: 
                print('Saliendo...')
                break
            case _:
                print_warning('Opción no válida. Por favor, intente de nuevo.')


if __name__ == "__main__":
    main()
