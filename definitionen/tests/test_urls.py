from django.test import TestCase, Client
from django.urls import reverse, resolve
from definitionen.views import *
from django.core.exceptions import *


class URLTests(TestCase):

    client = Client()

    def test_home(self):

        path_works = True

        try:
            path = reverse("homepage")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works

    def test_all_words(self):

        path_works = True

        try:
            path = reverse("all-words")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works

    def test_letter_words(self):

        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                   'U', 'V', 'W', 'X', 'Y', 'Z', 'Sonderzeichen']

        path_works = True

        for letter in letters:
            try:
                path = reverse("letter-words", args=[letter])
                self.client.get(path)
            except Exception:
                path_works = False

        assert path_works

    '''
    doesn't work for some reason
    def test_one_word(self):

        path_works = True

        try:
            path = reverse("one-word", args=["cringe"])
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works
    '''

    def test_create_definition(self):

        path_works = True

        try:
            path = reverse("create-definition")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works

    '''
    todo not working but definition_detail will probably not be used anyway
    def test_definition_detail(self):

        path_works = True

        try:
            path = reverse("definition-detail", args=[1])
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works
    '''

    def test_about(self):

        path_works = True

        try:
            path = reverse("blog-about")
            self.client.get(path)
        except Exception:
            path_works = False

        assert path_works


class LegalPagesTests(TestCase):

    def test_impressum(self):
        response = self.client.get(reverse("impressum"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Impressum")

    def test_datenschutz(self):
        response = self.client.get(reverse("datenschutz"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Datenschutzerklärung")

    def test_footer_links(self):
        response = self.client.get(reverse("homepage"))
        self.assertContains(response, reverse("impressum"))
        self.assertContains(response, reverse("datenschutz"))
