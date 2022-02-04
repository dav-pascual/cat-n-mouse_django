"""
@author: David Pascual
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ratonGato.settings')
django.setup()
from datamodel.models import Game, Move
from django.contrib.auth.models import User


def query_test():

    if User.objects.filter(id=10).exists() is False:
        user10 = User.objects.create_user(username='user10',
                                          password='user10',
                                          id=10)
    else:
        user10 = User.objects.get(id=10)

    if User.objects.filter(id=11).exists() is False:
        user11 = User.objects.create_user(username='user11',
                                          password='user11',
                                          id=11)
    else:
        user11 = User.objects.get(id=11)

    game10 = Game(cat_user=user10)
    game10.save()

    menor = Game.objects.first().id
    for game in Game.objects.all():
        if game.cat_user is not None and game.mouse_user is None:
            print(str(game))
            if game.id < menor:
                menor = game.id

    game11 = Game.objects.get(id=menor)
    game11.mouse_user = user11
    game11.save()
    print(str(game11))

    Move.objects.create(game=game11, player=game11.cat_user,
                        origin=2, target=11)
    print(str(game11))

    Move.objects.create(game=game11, player=game11.mouse_user,
                        origin=59, target=52)
    print(str(game11))


if __name__ == '__main__':
    print('Starting Query test...')
    query_test()
