from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from logic.forms import SignupForm, MoveForm, FilterSelectForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm as LoginForm
from django.contrib.auth import authenticate
from django.contrib.auth import login as user_login, logout as user_logout
from datamodel import constants
from datamodel.models import Counter, Game, User, Move
from datamodel.models import GameStatus, GameWinner, PlayerTypes
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import json


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)
    return wrapped


def login_required(f):
    def wrapped(request):
        if not request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to logged users"))
        else:
            return f(request)
    return wrapped


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    Counter.objects.inc()
    return render(request, "mouse_cat/error.html", context_dict)


def error404(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = "Page not found"
    Counter.objects.inc()
    return render(request, 'mouse_cat/error.html', context_dict)


def index(request):
    """
    @author: David Pascual
    Pagina de inicio.
    """
    return render(request, "mouse_cat/index.html")


@anonymous_required
def login(request):
    """
    @author: David Pascual
    Vista del login.
    """
    # Se recogen datos del formulario login mediante POST, si todo es correcto
    # se iniciara la sesion, sino se mostrara error al usuario.
    if request.method == 'POST':
        user_form = LoginForm(data=request.POST)

        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    user_login(request, user)
                    if 'next' in request.session:
                        next = request.session['next']
                        del request.session['next']
                        return redirect(next)
                    request.session['filter'] = False
                    return redirect(reverse('index'))

        user_form.add_error(None, "Username/password is not valid")

    # Se carga el formulario.
    else:
        user_form = LoginForm()

    return render(request,
                  'mouse_cat/login.html',
                  {'user_form': user_form})


@login_required
def logout(request):
    """
    @author: David Pascual
    Vista del logout.
    """
    if request.user.is_authenticated:
        user = request.user.username
    else:
        # Para evitar un error al abrir sesion previamente
        # de manera externa (ej. mediante admin)
        user = None

    user_logout(request)

    # Se borran variables de la sesion.
    if constants.GAME_SELECTED_SESSION_ID in request.session:
        del request.session[constants.GAME_SELECTED_SESSION_ID]
    if 'player_type' in request.session:
        del request.session['player_type']
    if 'status_selected' in request.session:
        del request.session['status_selected']
    if 'filter' in request.session:
        del request.session['filter']
    request.session.modified = True

    return render(request, "mouse_cat/logout.html", {'user': user})


@anonymous_required
def signup(request):
    """
    @author: David Pascual
    Vista del registro.
    """
    # Se recogen los datos del formulario mediante POST, si todo va bien,
    # el usuario queda registrado, y se inicia sesion.
    if request.method == 'POST':
        user_form = SignupForm(data=request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password')
            user = User(username=username, password=password)
            user.save()
            user.set_password(user.password)
            user.save()
            user_login(request, user)
            request.session['filter'] = False
            return render(request, 'mouse_cat/signup.html')
    # Se carga el formulario.
    else:
        user_form = SignupForm()

    return render(request,
                  'mouse_cat/signup.html',
                  {'user_form': user_form})


def create_game(request):
    """
    @author: David Pascual
    Vista para crear un juego.
    """
    if request.user.is_authenticated:
        game = Game(cat_user=request.user)
        game.save()
        return render(request, "mouse_cat/new_game.html", {'game': game})
    else:
        Counter.objects.inc()
        request.session['next'] = 'create_game'
        return redirect(reverse('login'))


def select_game(request, selected_game_id=-1,
                join_game_id=-1, playable_game_id=-1):
    """
    @author: David Pascual
    Vista para seleccionar un juego.
    """
    if not request.user.is_authenticated:
        Counter.objects.inc()
        request.session['next'] = 'select_game'
        return redirect(reverse('login'))

    # Si el juego ha sido seleccionado, se redirige para mostrar este,
    # o si el juego no existe se muestra error.
    if selected_game_id != -1:
        game = Game.objects.filter(id=selected_game_id)
        if (len(game) == 0 or game[0].status != GameStatus.ACTIVE or
            (game[0].cat_user != request.user and
             game[0].mouse_user != request.user)):
            context_dict = {}
            context_dict[constants.ERROR_MESSAGE_ID] = "Game does not exist"
            Counter.objects.inc()
            template = loader.get_template('mouse_cat/error.html')
            return HttpResponse(template.render(context_dict, request),
                                status=404)

        request.session[constants.GAME_SELECTED_SESSION_ID] = selected_game_id
        return redirect(reverse('show_game'))

    # Unirse al juego seleccionado, o si no se puede unir al juego se muestra
    # error.
    if join_game_id != -1:
        game = (Game.objects.filter(id=join_game_id)
                .filter(status=GameStatus.CREATED)
                .exclude(mouse_user__isnull=False))
        if len(game) == 0:
            context_dict = {}
            context_dict[constants.ERROR_MESSAGE_ID] = \
                "Game to join does not exist"
            Counter.objects.inc()
            template = loader.get_template('mouse_cat/error.html')
            return HttpResponse(template.render(context_dict, request),
                                status=404)
        game_join = Game.objects.get(id=join_game_id)
        game_join.mouse_user = request.user
        game_join.save()
        context_dict = {}
        context_dict['game_join'] = game_join
        return render(request, "mouse_cat/select_game.html",
                      {'game_join': game_join})

    # Reproducir juego seleccionado
    if playable_game_id != -1:
        game = (Game.objects.filter(id=playable_game_id)
                            .filter(status=GameStatus.FINISHED))
        if (len(game) == 0 or
            (game.cat_user != request.user and
             game.mouse_user != request.user)):
            context_dict = {}
            context_dict[constants.ERROR_MESSAGE_ID] = \
                "Game to play does not exist"
            Counter.objects.inc()
            template = loader.get_template('mouse_cat/error.html')
            return HttpResponse(template.render(context_dict, request),
                                status=404)

        request.session[constants.GAME_SELECTED_SESSION_ID] = playable_game_id
        request.session['move'] = 0
        board = [0] * (game.MAX_CELL + 1)
        board[0] = 1
        board[2] = 1
        board[4] = 1
        board[6] = 1
        board[59] = -1
        return render(request, "mouse_cat/play_game.html",
                      {'game': game, 'board': board})

    # Juegos para mostrar.
    if request.method == 'GET':
        # Juegos activos para jugar
        as_cat = (Game.objects.filter(cat_user=request.user)
                              .exclude(status=GameStatus.FINISHED)
                              .exclude(status=GameStatus.CREATED))
        as_mouse = (Game.objects.filter(mouse_user=request.user)
                                .exclude(status=GameStatus.FINISHED)
                                .exclude(status=GameStatus.CREATED))
        # Juegos para unirse como raton
        join_games = (Game.objects.filter(status=GameStatus.CREATED)
                      .exclude(mouse_user__isnull=False)
                      .exclude(cat_user=request.user))
        # Juegos para reproducir
        playable_games = (Game.objects.filter(status=GameStatus.FINISHED)
                                      .filter(Q(mouse_user=request.user) |
                                              Q(cat_user=request.user)))

        select_list = []

        # Aplicar filtro fisico si se ha solicitado
        select_form = FilterSelectForm(data=request.GET)
        if (select_form.is_valid() or
           (request.GET.get('page') and request.session['filter'])):
            if select_form.is_valid():
                player_type = select_form.cleaned_data.get('select_player')
                if player_type != 'all':
                    player_type = int(player_type)
                status_selected = select_form.cleaned_data.get('select_status')
                if status_selected != 'all':
                    status_selected = int(status_selected)
                request.session['player_type'] = player_type
                request.session['status_selected'] = status_selected
                request.session['filter'] = True
                request.session.modified = True
            else:
                # Recupera el filtro en caso de paginacion
                player_type = request.session['player_type']
                status_selected = request.session['status_selected']

            # Filtro seleccion
            if status_selected == GameStatus.CREATED:
                if (player_type == PlayerTypes.CAT or
                        player_type == PlayerTypes.MOUSE):
                    pass
                else:
                    select_list.extend(join_games)
            elif status_selected == GameStatus.ACTIVE:
                if player_type == PlayerTypes.CAT:
                    select_list.extend(as_cat)
                elif player_type == PlayerTypes.MOUSE:
                    select_list.extend(as_mouse)
                else:
                    select_list.extend(as_cat)
                    select_list.extend(as_mouse)
            elif status_selected == GameStatus.FINISHED:
                if player_type == PlayerTypes.CAT:
                    playable_games_cat = (playable_games
                                          .filter(cat_user=request.user))
                    select_list.extend(playable_games_cat)
                elif player_type == PlayerTypes.MOUSE:
                    playable_games_mouse = (playable_games
                                            .filter(mouse_user=request.user))
                    select_list.extend(playable_games_mouse)
                else:
                    select_list.extend(playable_games)
            else:
                if player_type == PlayerTypes.CAT:
                    select_list.extend(as_cat)
                    playable_games_cat = (playable_games
                                          .filter(cat_user=request.user))
                    select_list.extend(playable_games_cat)
                elif player_type == PlayerTypes.MOUSE:
                    select_list.extend(as_mouse)
                    playable_games_mouse = (playable_games
                                            .filter(mouse_user=request.user))
                    select_list.extend(playable_games_mouse)
                else:
                    select_list.extend(as_cat)
                    select_list.extend(as_mouse)
                    select_list.extend(join_games)
                    select_list.extend(playable_games)
        else:
            select_list.extend(as_cat)
            select_list.extend(as_mouse)
            select_list.extend(join_games)
            select_list.extend(playable_games)
            request.session['filter'] = False
            request.session.modified = True

        # Paginacion de la lista de juegos
        pags_select = Paginator(select_list, 5)
        page = request.GET.get('page')
        try:
            plist_select = pags_select.page(page)
        except (PageNotAnInteger, EmptyPage):
            plist_select = pags_select.page(1)

        context_dict = {}
        if plist_select:
            context_dict['select_list'] = plist_select

        select_form = FilterSelectForm()
        context_dict['select_form'] = select_form

        context_dict['GameStatus'] = GameStatus

        return render(request, "mouse_cat/select_game.html", context_dict)

    return render(request, "mouse_cat/select_game.html")


def show_game(request):
    """
    @author: David Pascual
    Vista encargada de mostrar el juego, con el tablero y los jugadores.
    """
    if request.user.is_authenticated:
        if constants.GAME_SELECTED_SESSION_ID in request.session:
            move_form = MoveForm()
            game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
            game = Game.objects.get(id=game_id)
            board = [0] * (game.MAX_CELL + 1)
            board[game.cat1] = 1
            board[game.cat2] = 1
            board[game.cat3] = 1
            board[game.cat4] = 1
            board[game.mouse] = -1
            # Si la partida ha finalizado, mostrar mensaje
            if game.status == GameStatus.FINISHED:
                if game.cat_user.id == request.user.id:
                    if game.winner == GameWinner.CAT:
                        messages.success(request,
                                         'Good game {}! You win the match.'
                                         .format(request.user.username))
                    elif game.winner == GameWinner.MOUSE:
                        messages.info(request, 'Game is over! {} wins.'
                                               .format(game.mouse_user
                                                       .username))
                else:
                    if game.winner == GameWinner.CAT:
                        messages.info(request, 'Game is over! {} wins.'
                                               .format(game.cat_user.username))
                    elif game.winner == GameWinner.MOUSE:
                        messages.success(request,
                                         'Good game {}! You win the match.'
                                         .format(request.user.username))
            return render(request, "mouse_cat/game.html",
                          {'game': game, 'move_form': move_form,
                           'board': board, 'GameStatus': GameStatus,
                           'GameWinner': GameWinner})
        else:
            context_dict = {}
            context_dict[constants.ERROR_MESSAGE_ID] = "No game selected"
            Counter.objects.inc()
            return render(request, "mouse_cat/error.html", context_dict)
    else:
        Counter.objects.inc()
        request.session['next'] = 'show_game'
        return redirect(reverse('login'))


def move(request):
    """
    @author: David Pascual
    Vista encargada de de procesar los movimientos de los jugadores.
    """
    # Se comprueba que el movimento sea correcto, en caso de error, se
    # muestra al usuario, sino se procesa tablero con el nuevo movimiento
    # realizado.
    if request.user.is_authenticated:
        if request.method == "POST":
            move_form = MoveForm(data=request.POST)

            if move_form.is_valid():
                if constants.GAME_SELECTED_SESSION_ID not in request.session:
                    context_dict = {}
                    error = "Service not found"
                    context_dict[constants.ERROR_MESSAGE_ID] = error
                    Counter.objects.inc()
                    template = loader.get_template('mouse_cat/error.html')
                    return HttpResponse(template.render(context_dict, request),
                                        status=404)
                origin = move_form.cleaned_data['origin']
                target = move_form.cleaned_data['target']
                game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
                game = Game.objects.get(id=game_id)
                player = request.user
                try:
                    Move.objects.create(game=game, player=player,
                                        origin=origin, target=target)
                except ValidationError:
                    move_form.add_error(None, "Move not allowed")

            game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
            game = Game.objects.get(id=game_id)
            board = [0] * (game.MAX_CELL + 1)
            board[game.cat1] = 1
            board[game.cat2] = 1
            board[game.cat3] = 1
            board[game.cat4] = 1
            board[game.mouse] = -1

            # Si la partida ha finalizado, mostrar mensaje
            if game.status == GameStatus.FINISHED:
                if game.cat_user.id == request.user.id:
                    if game.winner == GameWinner.CAT:
                        messages.success(request,
                                         'GOOD GAME {}! You win the match.'
                                         .format(request.user.username))
                    elif game.winner == GameWinner.MOUSE:
                        messages.info(request, 'Game is over! {} wins.'
                                               .format(game.mouse_user
                                                       .username))
                else:
                    if game.winner == GameWinner.CAT:
                        messages.info(request, 'Game is over! {} wins.'
                                               .format(game.cat_user.username))
                    elif game.winner == GameWinner.MOUSE:
                        messages.success(request,
                                         'GOOD GAME {}! You win the match.'
                                         .format(request.user.username))

            return render(request, "mouse_cat/game.html",
                          {'game': game, 'move_form': move_form,
                           'board': board, 'GameStatus': GameStatus,
                           'GameWinner': GameWinner})

        context_dict = {}
        context_dict[constants.ERROR_MESSAGE_ID] = "Service not found"
        Counter.objects.inc()
        template = loader.get_template('mouse_cat/error.html')
        return HttpResponse(template.render(context_dict, request), status=404)
    else:
        Counter.objects.inc()
        request.session['next'] = 'move'
        return redirect(reverse('login'))


def get_move(request):
    """
    @author: David Pascual
    Vista encargada de obtener movimientos para la reproduccion de un juego.
    """
    if request.method == 'POST':
        shift = int(request.POST.get('shift'))
        game = Game.objects.get(
            id=request.session[constants.GAME_SELECTED_SESSION_ID])
        move = Move.objects.filter(game=game)
        n_moves = len(move)

        if 'move' not in request.session:
            request.session['move'] = 0
        # Calculamos cual movimiento estan solicitando
        aux = request.session['move']
        if shift == -1:
            aux = aux + shift

        # Si pide uno antes que el primer movimiento o uno despues del ultimo
        if aux < 0 or aux >= n_moves:
            return HttpResponse('Error')
        # Obtenemos el movimiento
        move = move[aux]

        # Calculamos origen y destino
        if shift == -1:
            origin = move.target
            target = move.origin
        else:
            origin = move.origin
            target = move.target

        # Actualizamos el move guardado en sesion
        request.session['move'] = request.session['move'] + shift

        # Comprobamos si hay movimientos siguientes o previos
        if aux == 0 and shift == -1:
            previous = False
        else:
            previous = True
        if aux == n_moves - 1 and shift == 1:
            next = False
        else:
            next = True

        # Comprobamos de quien es el turno
        if game.cat_user == move.player:
            is_cat = True
        else:
            is_cat = False

        # Establecemos el ganador
        if game.winner == GameWinner.CAT:
            winner = str(game.cat_user)
        else:
            winner = str(game.mouse_user)

        return HttpResponse(json.dumps({'origin': origin, 'target': target,
                                        'previous': previous, 'next': next,
                                        'is_cat': is_cat, 'winner': winner}))
    else:
        context_dict = {}
        context_dict[constants.ERROR_MESSAGE_ID] = \
            "GET no permitido para este servicio."
        Counter.objects.inc()
        template = loader.get_template('mouse_cat/error.html')
        return HttpResponse(template.render(context_dict, request),
                            status=404)
