import logging
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Player, Game, Move

# Configurar el logger
logger = logging.getLogger(__name__)

# Create your tests here.

class PlayerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_create_player(self):
        response = self.client.post('/game/api/players/', {'name': 'TestPlayer'})
        
        # Verificar que la respuesta es 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        
        # Verificar el contenido de la respuesta
        self.assertIn('id', response_data)
        self.assertEqual(response_data['name'], 'TestPlayer')
        
        # Verificar que el jugador se ha creado en la base de datos
        self.assertEqual(Player.objects.count(), 1)
        self.assertEqual(Player.objects.get(id=response_data['id']).name, 'TestPlayer')


class GameTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.player1 = Player.objects.create(name='Player 1')
        self.player2 = Player.objects.create(name='Player 2')
        self.game = Game.objects.create(player1=self.player1, player2=self.player2, current_turn=self.player1)
        self.move_url = reverse('game-make-move', args=[self.game.id])
        self.position = 0
        self.out_range_position = 9
                                                                                                                                                                                                                                                                                                                                                
    def test_create_game(self):
        response = self.client.post('/game/api/games/', {
            'player1': self.player1.id,
            'player2': self.player2.id,
            'current_turn': self.player1.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verificar el contenido de la respuesta
        response_data = response.json()
        self.assertIn('id', response_data)
        self.assertEqual(response_data['player1'], self.player1.id)
        self.assertEqual(response_data['player2'], self.player2.id)
        self.assertEqual(response_data['current_turn'], self.player1.id)
        self.assertEqual(response_data['board'], '.........')

        # Verificar que se creó un único juego
        self.assertEqual(Game.objects.count(), 2) # Teniendo en cuenta que ya existe el de setUp 

        # Verificar que los datos en la base de datos coinciden con los de la respuesta
        game = Game.objects.get(id=response_data['id'])
        self.assertEqual(game.player1.id, self.player1.id)
        self.assertEqual(game.player2.id, self.player2.id)
        self.assertEqual(game.current_turn.id, self.player1.id)
        self.assertEqual(game.board, '.........')
    

    def test_make_move(self):
        response = self.client.post(self.move_url, {
            'player': self.player1.id,
            'position': self.position
        })
        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        
        # Verificar el contenido de la respuesta y el estado del juego
        self.assertEqual(response_data['board'][self.position], 'X')
        self.assertEqual(response_data['current_turn']['id'], self.player2.id)
        
        # Verificar que el movimiento se ha registrado en la base de datos
        self.game.refresh_from_db()
        self.assertEqual(self.game.board[self.position], 'X')
        self.assertEqual(self.game.current_turn.id, self.player2.id)
    
    def test_make_out_range_move(self):
        response = self.client.post(self.move_url, {
            'player': self.game.current_turn.id,
            'position': self.out_range_position
        })
        # Verificar que la respuesta es 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_make_move_in_taken_position(self):
        self.client.post(self.move_url, {
            'player': self.game.current_turn.id,
            'position': self.position
        })
        response = self.client.post(self.move_url, {
            'player': self.game.current_turn.id,
            'position': self.position
        })
        # Verificar que la respuesta es 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        
class MoveTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.player1 = Player.objects.create(name='Player 1')
        self.player2 = Player.objects.create(name='Player 2')
        self.game = Game.objects.create(player1=self.player1, player2=self.player2, current_turn=self.player1)

    def test_create_move(self):
        move = Move.objects.create(game=self.game, player=self.player1, position=0)
        
        # Verificar que el movimiento se ha creado
        self.assertEqual(Move.objects.count(), 1)
        self.assertEqual(move.position, 0)
        self.assertEqual(move.player.name, 'Player 1')