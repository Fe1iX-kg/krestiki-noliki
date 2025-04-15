from rest_framework import serializers
from .models import GameRoom, Game
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class GameRoomSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    opponent = UserSerializer(read_only=True, allow_null=True)

    class Meta:
        model = GameRoom
        fields = ['id', 'code', 'creator', 'opponent', 'is_active']
        read_only_fields = ['code', 'creator', 'opponent', 'is_active']

class GameSerializer(serializers.ModelSerializer):
    room = GameRoomSerializer(read_only=True)
    current_player = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Game
        fields = ['id', 'room', 'board', 'current_player', 'winner', 'is_finished']