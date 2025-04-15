from django.urls import path, include
from . import views

api_patterns = [
    path('', views.GameRoomViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', views.GameRoomViewSet.as_view({'get': 'retrieve'})),
    path('join/', views.GameRoomViewSet.as_view({'post': 'join'})),
    path('<int:pk>/game/', views.GameRoomViewSet.as_view({'get': 'game', 'post': 'move'})),
    path('<int:pk>/new_game/', views.GameRoomViewSet.as_view({'post': 'new_game'})),
    path('current_user/', views.GameRoomViewSet.as_view({'get': 'current_user'})),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('lobby/', views.lobby, name='lobby'),
    path('profile/', views.profile, name='profile'),
    path('game/<int:room_id>/', views.game, name='game'),
    path('api/rooms/', include((api_patterns, 'rooms'))),
    path('create-room-direct/', views.create_room_direct, name='create_room_direct'),
]