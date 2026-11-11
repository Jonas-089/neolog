from django.test import TestCase, Client
from django.urls import reverse
from definitionen.models import Definition, Word
from users.models import User
import json


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.mockuser = User.objects.create(id=4, username="anonym")
        self.mockword = Word.objects.create(word="debug test word")
        self.create_url = reverse("create-definition")

    def test_adding_definition(self):

        response = self.client.post(self.create_url, {
            "title": "debug test word",
            "content": "adding test word from debug",
            "example": "example of a test word from debug"
        })

        # checking if definition post got redirect response
        self.assertEqual(response.status_code, 302)

        # checking if definition was added to word
        self.assertEqual(self.mockword.definition_set.first().title, "debug test word")

    def test_adding_word(self):

        response = self.client.post(self.create_url, {
            "title": "adding definition without word",
            "content": "adding definition for which no word exists yet",
            "example": "this should result in a new word being created"
        })

        # checking if definition post got redirect response
        self.assertEqual(response.status_code, 302)

        # checking if word was added
        self.assertEqual(Definition.objects.last().word.word, "adding definition without word")

    # trying to add empty definition which should fail
    def test_adding_definition_no_data(self):

        response = self.client.post(self.create_url, {})

        # asserting that no definition could be created
        self.assertEqual(Definition.objects.count(), 0)
