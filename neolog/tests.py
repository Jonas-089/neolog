from django.test import TestCase, Client
from django.urls import reverse, resolve
from definitionen.views import *
from django.core.exceptions import *


class URLTests(TestCase):

    client = Client()

    def test_register(self):

        path_works = True

        try:
            path = reverse("register")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works

    '''
    todo doesn't work
    def test_profile(self):

        path_works = True

        try:
            path = reverse("profile")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works
    '''

    def test_login(self):

        path_works = True

        try:
            path = reverse("login")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works

    def test_logout(self):

        path_works = True

        try:
            path = reverse("logout")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works