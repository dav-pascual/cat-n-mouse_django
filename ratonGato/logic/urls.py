from django.urls import path
from logic import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.index, name='landing'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('create_game/', views.create_game, name='create_game'),
    path('select_game/game/<int:selected_game_id>/',
         views.select_game, name='selected_game'),
    path('select_game/join_game/<int:join_game_id>/',
         views.select_game, name='join_game'),
    path('select_game/play_game/<int:playable_game_id>/',
         views.select_game, name='play_game'),
    path('select_game/', views.select_game, name='select_game'),
    path('show_game/', views.show_game, name='show_game'),
    path('move/', views.move, name='move'),
    path('get_move/', views.get_move, name='get_move')
]
