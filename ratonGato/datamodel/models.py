from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime


class PlayerTypes:
    """
    @author: David Pascual
    Tipos de jugadores
    """
    CAT = 0
    MOUSE = 1

    def __str__(self):
        return ("Player types: Cat = {}, Mouse = {}"
                .format(self.CAT, self.MOUSE))


class GameStatus:
    """
    @author: David Pascual
    Tipos de la variable status segun el estado de la partida.
    """
    FINISHED = 0
    CREATED = 1
    ACTIVE = 2

    def __str__(self):
        return ("Status types: FINISHED = {}, CREATED = {}, ACTIVE = {}"
                .format(self.FINISHED, self.CREATED, self.ACTIVE))


class GameWinner:
    """
    @author: David Pascual
    Tipos de la variable winner según el estado de la partida.
    """
    UNFINISHED = 0
    CAT = 1
    MOUSE = 2

    def __str__(self):
        return ("Winner types: UNFINISHED = {}, CAT = {}, MOUSE = {}"
                .format(self.UNFINISHED, self.CAT, self.MOUSE))


def check_win(cat1, cat2, cat3, cat4, mouse):
    """
    @author: David Pascual
    Comprueba si las posiciones de los ratones/gato corresponden a una
    situación de ganar la partida.
    """
    mouse_moves = [-7, -9, 7, 9]

    aux_mouse = mouse // 8
    # Gana raton
    if (aux_mouse < cat1 // 8 and aux_mouse < cat2 // 8 and
            aux_mouse < cat3 // 8 and aux_mouse < cat4 // 8):
        return GameWinner.MOUSE

    # Comprobamos si en todos los posibles movimientos del raton hay un gato
    flag = 1
    for item in mouse_moves:
        aux = mouse + item
        if aux >= 0 and aux < 64:
            if aux == cat1 or aux == cat2 or aux == cat3 or aux == cat4:
                continue

            # Si hay un movimiento posible, los gatos no han ganado
            else:
                flag = 0
                break

    # La bandera no ha cambiado, por tanto, los gatos han ganado
    if flag == 1:
        return GameWinner.CAT

    # Si no, nadie gana continua juego
    return GameWinner.UNFINISHED


def is_valid_cell(posicion, game_aux):
    """
    @author: David Pascual
    Comprueba que una posición del tablero es valida (dentro de los limites
    y que sea blanca).
    """
    # Comprobamos que no se salga del tablero
    if posicion < game_aux.MIN_CELL or posicion > game_aux.MAX_CELL:
        return False
    # Comprobamos que sea blanca
    columna = posicion % 8
    fila = posicion // 8
    if (columna + fila) % 2 == 0:
        return True
    return False


class Game(models.Model):
    """
    @author: David Pascual
    Modelo de datos para Game.
    """

    cat_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="games_as_cat",
                                 null=True, blank=False)
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name="games_as_mouse",
                                   null=True, blank=True)
    cat1 = models.IntegerField(default=0)
    cat2 = models.IntegerField(default=2)
    cat3 = models.IntegerField(default=4)
    cat4 = models.IntegerField(default=6)
    mouse = models.IntegerField(default=59)
    cat_turn = models.BooleanField(default=True)
    status = models.IntegerField(default=GameStatus.CREATED)
    winner = models.IntegerField(default=GameWinner.UNFINISHED)
    MIN_CELL = 0
    MAX_CELL = 63

    def clean(self):
        """
        Validaciones de datos: posicion no valida, status no valido, empezar
        la partida si se detecta un raton y poner partida a status FINISHED si
        se ha terminado.
        LLamada siempre con save.
        """
        if (is_valid_cell(self.cat1, self) is False or
                is_valid_cell(self.cat2, self) is False or
                is_valid_cell(self.cat3, self) is False or
                is_valid_cell(self.cat4, self) is False or
                is_valid_cell(self.mouse, self) is False):
            raise ValidationError('Invalid cell for a cat or the mouse')

        if (self.status != GameStatus.CREATED and
                self.status != GameStatus.ACTIVE and
                self.status != GameStatus.FINISHED):
            raise ValidationError('Game status not valid')

        if self.mouse_user is not None:
            if self.status == GameStatus.CREATED:
                self.status = GameStatus.ACTIVE

        if (self.winner != GameWinner.UNFINISHED and
                self.winner != GameWinner.CAT and
                self.winner != GameWinner.MOUSE):
            raise ValidationError('Winner status not valid')

        if (self.status != GameStatus.FINISHED and
                self.winner != GameWinner.UNFINISHED):
            raise ValidationError(
                'There cannot be a winner in an unfinished game.')

        win_status = check_win(self.cat1, self.cat2, self.cat3,
                               self.cat4, self.mouse)
        if win_status == GameWinner.CAT:
            self.status = GameStatus.FINISHED
            self.winner = GameWinner.CAT
        elif win_status == GameWinner.MOUSE:
            self.status = GameStatus.FINISHED
            self.winner = GameWinner.MOUSE

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except ValidationError as e:
            raise ValidationError(e)
        super(Game, self).save(*args, **kwargs)

    def __str__(self):
        if self.status == GameStatus.CREATED:
            current_status = 'Created'
        elif self.status == GameStatus.ACTIVE:
            current_status = 'Active'
        elif self.status == GameStatus.FINISHED:
            current_status = 'Finished'

        if self.cat_turn is True:
            cross_cat = 'X'
            cross_mouse = ' '
        else:
            cross_cat = ' '
            cross_mouse = 'X'

        if self.mouse_user is not None:
            return ("({}, {})\tCat [{}] {}({}, {}, {}, {})"
                    " --- Mouse [{}] {}({})"
                    .format(self.id, current_status, cross_cat,
                            str(self.cat_user), self.cat1, self.cat2,
                            self.cat3, self.cat4, cross_mouse,
                            str(self.mouse_user),
                            self.mouse))

        return ("({}, {})\tCat [{}] {}({}, {}, {}, {})"
                .format(self.id, current_status, cross_cat, str(self.cat_user),
                        self.cat1, self.cat2, self.cat3, self.cat4))


# Comprueba si un movimiento se puede hacer
def check_move(origin, target, is_cat, game_aux):
    """
    @author: David Pascual
    Validacion de movimiento correcto segun las reglas del
    juego para gato y raton.
    """
    if origin is None or target is None:
        return False

    if (is_valid_cell(origin, game_aux) is False or
            is_valid_cell(target, game_aux) is False):
        return False

    if (target == game_aux.cat1 or target == game_aux.cat2 or
        target == game_aux.cat3 or target == game_aux.cat4 or
            target == game_aux.mouse):
        return False

    mouse_moves = [-7, -9, 7, 9]
    cat_moves = [7, 9]

    if is_cat is True:
        aux_moves = cat_moves
    else:
        aux_moves = mouse_moves

    for item in aux_moves:
        aux = origin + item
        if (aux >= 0 and aux <= 63 and
                is_valid_cell(aux, game_aux) is True and aux == target):
            return True

    return False


class Move(models.Model):
    """
    @author: David Pascual
    Modelo de datos de Move.
    """
    origin = models.IntegerField(blank=False)
    target = models.IntegerField(blank=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name="moves", blank=False)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Validacion de datos para un movimiento.
        Error si el juego no esta activo, el move
        no pertecene al turno correcto, el movimiento es ilegal segun reglas,
        o la posicion origen es incorrecta.
        """
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError("Move not allowed")

        if self.player == self.game.cat_user:
            if self.game.cat_turn is not True:
                raise ValidationError("Move not allowed")

            if (check_move(self.origin, self.target, True, game_aux=self.game)
                    is False):
                raise ValidationError("Move not allowed")

            # Asignacion target
            if self.origin == self.game.cat1:
                self.game.cat1 = self.target
            elif self.origin == self.game.cat2:
                self.game.cat2 = self.target
            elif self.origin == self.game.cat3:
                self.game.cat3 = self.target
            elif self.origin == self.game.cat4:
                self.game.cat4 = self.target
            else:
                # Posicion origen incorrecta
                raise ValidationError('Move not allowed')

            self.game.cat_turn = False
            self.date = datetime.date.today()

        else:
            if self.game.cat_turn is True:
                raise ValidationError("Move not allowed")

            if self.origin == self.game.mouse:
                if (check_move(self.origin, self.target, False,
                               game_aux=self.game) is False):
                    raise ValidationError("Move not allowed")

                self.game.mouse = self.target
                self.game.cat_turn = True
                self.date = datetime.date.today()
            else:
                # Posicion origen incorrecta
                raise ValidationError('Move not allowed')
        self.game.save()
        super(Move, self).save(*args, **kwargs)

    def __str__(self):
        return ("Move: Origin={}, Target={}, GameId={}, PlayerId={}, Date={}"
                .format(self.origin, self.target, self.game.id, self.player.id,
                        self.date))


class CounterManager(models.Manager):
    """
    @author: David Pascual
    Clase Manager para el objeto del modelo counter.
    Se encargara de todas las modificaciones referentes a este objeto.
    """

    def get_current_value(self):
        aux = self.get_queryset()
        if not aux:
            return 0
        return aux[0].value

    def inc(self):
        aux = self.get_queryset()
        if not aux:
            counter = Counter()
            super(Counter, counter).save()
        else:
            counter = aux[0]
        counter.value += 1
        super(Counter, counter).save()
        return counter.value


class Counter(models.Model):
    """
    @author: David Pascual
    Modelo counter, que almacena un contador independiente del
    usuario y sesion, que se podra incrementar, leer e inicializar.
    """
    value = models.IntegerField(null=False, default=0)
    objects = CounterManager()

    def save(self, *args, **kwargs):
        raise ValidationError("Insert not allowed")
