from rest_framework import serializers
from .models import Player, Game, Move

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = '__all__'

class GameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    player1 = PlayerSerializer()
    player2 = PlayerSerializer()
    current_turn = PlayerSerializer()
    winner = PlayerSerializer()
    moves = MoveSerializer(many=True, read_only=True)
    
    class Meta:
        model = Game
        fields = '__all__'
