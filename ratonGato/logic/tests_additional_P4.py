"""
@author: David Pascual
"""
from datamodel.models import Counter
from django.urls import reverse
from . import tests_services

GET_MOVE_SERVICE = "get_move"
LOGOUT_SERVICE = "logout"
CREATE_GAME_SERVICE = "create_game"
SELECT_GAME_SERVICE = "select_game"
SHOW_GAME_SERVICE = "show_game"
MOVE_SERVICE = "move"
LOGIN_SERVICE = "login"
SIGNUP_SERVICE = "signup"


class CounterErrorTests(tests_services.PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Counter cuenta las operaciones no autorizadas
            de los servicios basicos """
        self.logoutTestUser(self.client1)
        n_counter = Counter.objects.get_current_value()

        # Logout sin sesion iniciada
        self.client1.get(reverse(LOGOUT_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        # Crear game sin sesion iniciada
        self.client1.get(reverse(CREATE_GAME_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        # Select game sin sesion iniciada
        self.client1.get(reverse(SELECT_GAME_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        # Show game sin sesion iniciada
        self.client1.get(reverse(SHOW_GAME_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        # Move sin sesion iniciada
        self.client1.get(reverse(MOVE_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        # Get move sin sesion iniciada
        self.client1.get(reverse(GET_MOVE_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        self.loginTestUser(self.client1, self.user1)

        # Login con la sesion ya iniciada
        self.client1.get(reverse(LOGIN_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)

        # Sign Up con la sesion ya iniciada
        self.client1.get(reverse(SIGNUP_SERVICE), follow=True)
        n_counter += 1
        self.assertEqual(Counter.objects.get_current_value(), n_counter)
