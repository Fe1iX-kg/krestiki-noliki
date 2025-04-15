from django.db import models
from django.contrib.auth.models import User

class GameRoom(models.Model):
    code = models.CharField(max_length=6, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='joined_rooms')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.code}"

class Game(models.Model):
    room = models.OneToOneField(GameRoom, on_delete=models.CASCADE)
    board = models.CharField(max_length=9, default='         ')
    current_player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='games_as_current_player')
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='games_won')
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"Game in {self.room.code}"