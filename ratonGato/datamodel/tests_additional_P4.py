"""
@author: David Pascual
"""
from . import tests
from .models import Game, GameStatus, Move, GameWinner
from django.core.exceptions import ValidationError


class GameEndTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Gana raton, y despues de ganar,
            no se pueden hacer mas movimientos."""
        game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1],
            status=GameStatus.ACTIVE)

        moves = [
            {"player": self.users[0], "origin": 0, "target": 9},
            {"player": self.users[1], "origin": 59, "target": 50},
            {"player": self.users[0], "origin": 2, "target": 11},
            {"player": self.users[1], "origin": 50, "target": 43},
            {"player": self.users[0], "origin": 4, "target": 13},
            {"player": self.users[1], "origin": 43, "target": 36},
            {"player": self.users[0], "origin": 6, "target": 15},
            {"player": self.users[1], "origin": 36, "target": 27},
            {"player": self.users[0], "origin": 11, "target": 18},
            {"player": self.users[1], "origin": 27, "target": 20},
            {"player": self.users[0], "origin": 13, "target": 22},
            {"player": self.users[1], "origin": 20, "target": 11},
            {"player": self.users[0], "origin": 22, "target": 31},
            {"player": self.users[1], "origin": 11, "target": 4},
        ]

        illegal_moves = [
            {"player": self.users[0], "origin": 31, "target": 38},
            {"player": self.users[1], "origin": 4, "target": 13},
        ]

        # Movimientos para ganar la partida
        for move in moves:
            Move.objects.create(
                game=game, player=move["player"], origin=move["origin"],
                target=move["target"])

        self.assertEqual(GameStatus.FINISHED, game.status)
        self.assertEqual(GameWinner.MOUSE, game.winner)

        extra_moves = 0

        # Movimientos tras finalizar partida que deben lanzar una excepcion
        try:
            Move.objects.create(
                game=game, player=illegal_moves[0]["player"],
                origin=illegal_moves[0]["origin"],
                target=move["target"])
        except ValidationError as e:
            self.assertEqual(e.message, 'Move not allowed')
        else:
            raise Exception('Illegal move allowed')

        extra_moves += 1
        self.assertNotEqual(game.moves.count(), extra_moves)

        try:
            Move.objects.create(
                game=game, player=illegal_moves[1]["player"],
                origin=illegal_moves[1]["origin"],
                target=move["target"])
        except ValidationError as e:
            self.assertEqual(e.message, 'Move not allowed')
        else:
            raise Exception('Illegal move allowed')

        self.assertNotEqual(game.moves.count(), extra_moves)
        extra_moves += 1
        self.assertNotEqual(game.moves.count(), extra_moves)

    def test2(self):
        """ Gana gato, y despues de ganar,
            no se pueden hacer mas movimientos."""
        game = Game.objects.create(
            cat_user=self.users[0], mouse_user=self.users[1],
            status=GameStatus.ACTIVE)

        moves = [
            {"player": self.users[0], "origin": 0, "target": 9},
            {"player": self.users[1], "origin": 59, "target": 50},
            {"player": self.users[0], "origin": 2, "target": 11},
            {"player": self.users[1], "origin": 50, "target": 43},
            {"player": self.users[0], "origin": 4, "target": 13},
            {"player": self.users[1], "origin": 43, "target": 36},
            {"player": self.users[0], "origin": 6, "target": 15},
            {"player": self.users[1], "origin": 36, "target": 27},
            {"player": self.users[0], "origin": 9, "target": 18},
            {"player": self.users[1], "origin": 27, "target": 20},
            {"player": self.users[0], "origin": 15, "target": 22},
            {"player": self.users[1], "origin": 20, "target": 29},
            {"player": self.users[0], "origin": 18, "target": 27},
            {"player": self.users[1], "origin": 29, "target": 20},
            {"player": self.users[0], "origin": 22, "target": 29},
        ]

        illegal_moves = [
            {"player": self.users[1], "origin": 29, "target": 38},
            {"player": self.users[0], "origin": 20, "target": 29},
        ]

        # Movimientos para ganar la partida
        for move in moves:
            Move.objects.create(
                game=game, player=move["player"], origin=move["origin"],
                target=move["target"])

        self.assertEqual(GameStatus.FINISHED, game.status)
        self.assertEqual(GameWinner.CAT, game.winner)

        extra_moves = 0

        # Movimientos tras finalizar partida que deben lanzar una excepcion
        try:
            Move.objects.create(
                game=game, player=illegal_moves[0]["player"],
                origin=illegal_moves[0]["origin"],
                target=move["target"])
        except ValidationError as e:
            self.assertEqual(e.message, 'Move not allowed')
        else:
            raise Exception('Illegal move allowed')

        extra_moves += 1
        self.assertNotEqual(game.moves.count(), extra_moves)

        try:
            Move.objects.create(
                game=game, player=illegal_moves[1]["player"],
                origin=illegal_moves[1]["origin"],
                target=move["target"])
        except ValidationError as e:
            self.assertEqual(e.message, 'Move not allowed')
        else:
            raise Exception('Illegal move allowed')

        self.assertNotEqual(game.moves.count(), extra_moves)
        extra_moves += 1
        self.assertNotEqual(game.moves.count(), extra_moves)
