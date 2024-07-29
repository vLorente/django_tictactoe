from django.db import models

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self) -> str:
        return self.name

class Game(models.Model):
    STATES = {
        "progress": "In Progress",
        "finished": "Finished",
    }

    player1 = models.ForeignKey(Player, related_name='player1_games', on_delete=models.CASCADE, )
    player2 = models.ForeignKey(Player, related_name='player2_games', on_delete=models.CASCADE)
    board = models.CharField(max_length=9, default='.........')
    current_turn = models.ForeignKey(Player, related_name='current_turn_games', on_delete=models.CASCADE, blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATES, default="progress")
    winner = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL)
    

    def __str__(self) -> str:
        return f'{self.id} - Game between {self.player1.name} and {self.player2.name}: {self.state}'
    
    # Si no se indica valor, valor por defecto player1
    def save(self, *args, **kwargs):
        if not self.current_turn:
            self.current_turn = self.player1
        super(Game, self).save(*args, **kwargs)
    
    def check_winner(self):
        win_conditions = [
            # filas
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            # columnas
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            # diagonales
            [0, 4, 8],
            [2, 4, 6]
        ]
        
        for condition in win_conditions:
            if self.board[condition[0]] != '.' and self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]]:
                return self.player1 if self.board[condition[0]] == 'X' else self.player2
        
        return None

    
class Move(models.Model):
    game = models.ForeignKey(Game, related_name='moves', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='moves', on_delete=models.CASCADE)
    position = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'Move made by {self.player.name} in game {self.game.id}'