from django.test import TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from users.views import *
from definitionen.models import *


class URLTests(StaticLiveServerTestCase):

    def setUp(self):
        self.client = Client()
        self.anon = User.objects.create(id=4, username="anonym")
        self.jonas = User.objects.create(id=1, username="jonas")
        self.client.force_login(self.jonas)
        self.mockword = Word.objects.create(word="debug test word")
        self.create_url = reverse("create-definition")

    def test_profile(self):

        path_works = True

        try:
            path = reverse("profile", args=["jonas"])
            self.client.get(path)
        except Exception:
            # path_works = False
            assert False

        assert path_works
