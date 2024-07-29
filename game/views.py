import logging
from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Player, Game, Move
from .serializers import PlayerSerializer, GameSerializer, GameCreateSerializer

# Configurar el logger
logger = logging.getLogger(__name__)

# Create your views here.

class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['state', 'player1', 'player2']

    def get_serializer_class(self):
        if self.action == 'create':
            return GameCreateSerializer
        return GameSerializer
        
    @action(detail=True, methods=['post'])
    def make_move(self, request, pk=None):
        game = self.get_object()
        player_id = int(request.data.get('player'))
        position = int(request.data.get('position'))

        # Validar usuario
        try:
            player = Player.objects.get(id=player_id)
        except Player.DoesNotExist:
            return Response({'detail': 'Player not found.'}, status=status.HTTP_404_NOT_FOUND)
        if game.player1 != player and game.player2 != player:
            return Response({'detail': f'Player "{player.name}" not in the game.'})
        
        # Validar movimiento
        if game.current_turn != player:
            logger.error(f'Not your turn')
            return Response({'detail': 'Not your turn.'}, status=status.HTTP_400_BAD_REQUEST)
        if position not in range(0,9):
            logger.error(f'Invalid position')
            return Response({'detail': 'Invalid position.'}, status=status.HTTP_400_BAD_REQUEST)
        if game.board[position] != '.':
            logger.error(f'Invalid move, position already taken')
            return Response({'detail': 'Invalid move, position already taken.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Realizar movimiento
        arr_board = list(game.board)
        arr_board[position] = 'X' if game.current_turn == game.player1 else 'O'
        game.board = ''.join(arr_board)
        
        # Verificar el estado de la partida
        winner = game.check_winner()
        
        if winner:
            game.state = 'finished'
            game.winner = winner
        elif not winner and '.' not in game.board:
            game.state = 'finished'
        else:
            game.current_turn = game.player2 if game.current_turn == game.player1 else game.player1
        
        game.save()
        
        Move.objects.create(game=game, player=player, position=position)
        
        return Response(GameSerializer(game).data)