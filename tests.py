from django.test import TestCase
from django.urls import reverse

from .models import *


# Create your tests here.

def _creds(username, password):
    return {'username': username, 'password': password}


class TestUserCreation(TestCase):
    def test_create_users(self):
        '''
        Tries creating 2 users
        '''

        params = {'username': 'Alice',
                  'email': 'alice@yopmail.com',
                  'password1': 'passwordalice',
                  'password2': 'passwordalice'}
        self.client.post(reverse('rebellion:create_account'), params)
        self.client.get(reverse('rebellion:logout'))

        self.assertEquals(len(User.objects.filter(username='Alice')), 1)

        params = {'username': 'Bob',
                  'email': 'bob@yopmail.com',
                  'password1': 'passwordbob',
                  'password2': 'passwordbob'}
        self.client.post(reverse('rebellion:create_account'), params)
        self.client.get(reverse('rebellion:logout'))

        self.assertEquals(len(User.objects.filter(username='Bob')), 1)
        self.assertEquals(len(User.objects.all()), 2)

    def test_create_users_fails(self):
        """
        Tries creating a user with invalid input
        """

        params = {'username': 'Alice',  # already exists
                  'email': 'alice@yopmail.com',
                  'password1': 'passwordalice',
                  'password2': 'passwordalice'}
        self.client.post(reverse('rebellion:create_account'), params)
        self.client.get(reverse('rebellion:logout'))
        params['email'] = 'alice2@yopmail.com'
        self.client.post(reverse('rebellion:create_account'), params)
        self.client.get(reverse('rebellion:logout'))

        # Can't create two users with same username
        self.assertEquals(len(User.objects.filter(username='Alice', email='alice@yopmail.com')), 1)
        self.assertEquals(len(User.objects.filter(username='Alice', email='alice2@yopmail.com')), 0)

        params = {'username': 'Cynthia',
                  'email': 'cynthia@yopmail.com',
                  'password1': 'passwordcynthia',
                  'password2': 'passwordfail'}  # Fail
        self.client.post(reverse('rebellion:create_account'), params)
        self.client.get(reverse('rebellion:logout'))

        # Creation fails if passwords are not identical
        self.assertEquals(len(User.objects.filter(username='Cynthia')), 0)
        self.assertEquals(len(User.objects.all()), 1)


class TestPendingGame(TestCase):
    def setUp(self):
        self.alice_creds = _creds("Alice", "passwordalice")
        self.bob_creds = _creds("Bob", "passwordbob")
        self.claire_creds = _creds("Claire", "passwordclaire")

        User.objects.create_user(username="Alice", password="passwordalice")
        User.objects.create_user(username="Bob", password="passwordbob")
        User.objects.create_user(username="Claire", password="passwordclaire")

    def test_create_pending_game(self):
        self.client.post(reverse('rebellion:login'), self.alice_creds)
        self.client.post(reverse('rebellion:create_pending_game'))

        alice = User.objects.get(username='Alice')
        self.assertEquals(len(PendingGame.objects.filter(owner=alice)), 1)

    def test_create_pending_game_fail(self):
        self.client.post(reverse('rebellion:login'), self.alice_creds)
        self.client.post(reverse('rebellion:create_pending_game'))
        self.client.post(reverse('rebellion:create_pending_game'))

        # One user Can't create two pending games
        alice = User.objects.get(username='Alice')
        self.assertEquals(len(PendingGame.objects.filter(owner=alice)), 1)

        self.client.get(reverse('rebellion:logout'))
        self.client.post(reverse('rebellion:create_pending_game'))
        # Can't create a game if not logged in
        self.assertEquals(len(PendingGame.objects.all()), 1)

    def test_join(self):
        self.client.post(reverse('rebellion:login'), self.alice_creds)
        self.client.post(reverse('rebellion:create_pending_game'))
        self.client.post(reverse('rebellion:logout'))
        self.client.post(reverse('rebellion:login'), self.bob_creds)
        self.client.post(reverse('rebellion:join_game'), {'pgame_id': '1'})

        alice = User.objects.get(username='Alice')
        bob = User.objects.get(username='Bob')
        self.assertEquals(len(PendingGame.objects.filter(owner=alice, joiner=bob)), 1)

    def test_join_fail(self):
        self.client.post(reverse('rebellion:login'), self.alice_creds)
        self.client.post(reverse('rebellion:create_pending_game'))

        # One can't join his own game
        self.client.post(reverse('rebellion:join_game'), {'pgame_id': '1'})
        alice = User.objects.get(username='Alice')
        self.assertEquals(len(PendingGame.objects.filter(owner=alice, joiner=alice)), 0)

        # Can't join if not logged in
        self.client.post(reverse('rebellion:logout'))
        self.client.post(reverse('rebellion:join_game'), {'pgame_id': '1'})
        self.assertIsNone(PendingGame.objects.get(id='1').joiner)

        # Can't join if someone already joined
        self.client.post(reverse('rebellion:login'), self.bob_creds)
        self.client.post(reverse('rebellion:join_game'), {'pgame_id': '1'})
        self.client.post(reverse('rebellion:logout'))
        self.client.post(reverse('rebellion:login'), self.claire_creds)
        self.client.post(reverse('rebellion:join_game'), {'pgame_id': '1'})
        bob = User.objects.get(username='Bob')
        claire = User.objects.get(username='Claire')
        self.assertEquals(len(PendingGame.objects.filter(owner=alice, joiner=bob)), 1)
        self.assertEquals(len(PendingGame.objects.filter(owner=alice, joiner=claire)), 0)
