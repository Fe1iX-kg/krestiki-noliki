from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action  # Убираем permission_classes из импорта
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import GameRoom, Game
from .serializers import GameRoomSerializer, GameSerializer
import random
import string

def index(request):
    return render(request, 'index.html')

@login_required
def lobby(request):
    return render(request, 'lobby.html')

@login_required
def profile(request):
    created_rooms = GameRoom.objects.filter(creator=request.user)
    joined_rooms = GameRoom.objects.filter(opponent=request.user)
    return render(request, 'profile.html', {
        'created_rooms': created_rooms,
        'joined_rooms': joined_rooms
    })

@login_required
def game(request, room_id):
    room = get_object_or_404(GameRoom, id=room_id, is_active=True)
    return render(request, 'game.html', {'room_id': room_id, 'room_code': room.code})

class GameRoomViewSet(viewsets.ModelViewSet):
    queryset = GameRoom.objects.all()
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]  # По умолчанию требуется авторизация

    def get_permissions(self):
        """
        Динамически задаём разрешения в зависимости от действия.
        """
        if self.action in ['join', 'game', 'move']:  # Разрешаем join, game и move для неавторизованных
            return [AllowAny()]
        return super().get_permissions()

    # ... остальные методы без изменений ...
    # ... остальные методы без изменений ...
    def perform_create(self, serializer):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            from django.contrib.auth.models import User
            user, _ = User.objects.get_or_create(username='guest')
        serializer.save(creator=user, code=code)

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        if request.user.is_authenticated:
            return Response({'username': request.user.username, 'id': request.user.id})
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def join(self, request):
        code = request.data.get('code')
        print(f"Received code: {code}")
        try:
            room = GameRoom.objects.get(code=code, is_active=True)
            print(f"Found room: {room.code}, ID: {room.id}")
            user = self.request.user if self.request.user.is_authenticated else None
            if not user:
                from django.contrib.auth.models import User
                user, _ = User.objects.get_or_create(username='guest')
            print(f"User trying to join: {user.username if user else 'None'} (ID: {user.id if user else 'None'})")
            print(f"Room creator: {room.creator.username} (ID: {room.creator.id})")
            if room.opponent is None:
                print(f"Setting opponent to: {user.username if user else 'None'}")
                room.opponent = user
                room.save()
                room.refresh_from_db()
                print(f"Opponent after save: {room.opponent.username if room.opponent else 'None'}")
                game, created = Game.objects.get_or_create(room=room, defaults={'current_player': room.creator, 'board': '         '})
                print(f"Game object: {game}, Created: {created}")
                serialized_room = GameRoomSerializer(room).data
                print(f"Serialized room data: {serialized_room}")
                return Response({'status': 'joined', 'room': serialized_room})
            print("Room is full")
            return Response({'error': 'Room is full'}, status=status.HTTP_400_BAD_REQUEST)
        except GameRoom.DoesNotExist:
            print(f"Room with code {code} not found or not active")
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"])
    def game(self, request, pk=None):
        room = get_object_or_404(GameRoom, id=pk)
        game = get_object_or_404(Game, room=room)
        return Response(GameSerializer(game).data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        print(f"Received move: pk={pk}, data={request.data}")
        try:
            room = GameRoom.objects.get(id=pk)
            print(f"Room: {room}, Creator: {room.creator}, Opponent: {room.opponent}")
        except GameRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            game = Game.objects.get(room=room)
            print(f"Game: {game}, Board: {game.board}, Current Player: {game.current_player}")
        except Game.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

        if game.is_finished:
            return Response({'error': 'Game is finished'}, status=status.HTTP_400_BAD_REQUEST)

        index = request.data.get('index')
        print(f"Index: {index}, Type: {type(index)}")
        if not isinstance(index, int) or index < 0 or index > 8:
            return Response({'error': 'Invalid move'}, status=status.HTTP_400_BAD_REQUEST)

        board = list(game.board)
        if board[index] != ' ':
            return Response({'error': 'Cell already taken'}, status=status.HTTP_400_BAD_REQUEST)

        if not game.current_player or not room.creator:
            return Response({'error': 'Invalid game state'}, status=status.HTTP_400_BAD_REQUEST)

        symbol = 'X' if game.current_player == room.creator else 'O'
        board[index] = symbol
        game.board = ''.join(board)

        wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for w in wins:
            if board[w[0]] == board[w[1]] == board[w[2]] != ' ':
                game.winner = game.current_player
                game.is_finished = True
                break
        if ' ' not in board and not game.winner:
            game.is_finished = True

        if not game.is_finished:
            game.current_player = room.opponent if room.opponent and game.current_player == room.creator else room.creator

        game.save()
        print(f"Move made: Board: {game.board}, Current Player: {game.current_player}, Winner: {game.winner}")
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def new_game(self, request, pk=None):
        room = GameRoom.objects.get(id=pk)
        game = Game.objects.get(room=room)
        game.board = '         '
        game.current_player = room.creator
        game.winner = None
        game.is_finished = False
        game.save()
        return Response({'status': 'success'})

@login_required
def create_room_direct(request):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    user = request.user if request.user.is_authenticated else None
    if not user:
        from django.contrib.auth.models import User
        user, _ = User.objects.get_or_create(username='guest')
    room = GameRoom.objects.create(creator=user, code=code, is_active=True)
    return render(request, 'room_created.html', {'room_code': code, 'room_id': room.id})