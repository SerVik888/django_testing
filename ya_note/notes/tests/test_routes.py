from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from notes.models import Note, User


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Я')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='i_5',
            author=cls.author
        )
        cls.urls_with_args = (
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,))
        )
        cls.urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            *cls.urls_with_args
        )

    def test_pages_availability(self):
        """Доступность страниц анонимному пользователю"""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for url in urls:
            with self.subTest("Страница не доступна", url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_availability_for_author_client(self):
        """Доступность страниц для автора заметок"""
        for name, args in self.urls:
            with self.subTest("Страница не доступна", name=name):
                self.client.force_login(self.author)
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_availability_for_reader_client(self):
        """Доступность страниц для читателя заметок"""
        for name, args in self.urls_with_args:
            with self.subTest("Страница не доступна", name=name):
                self.client.force_login(self.reader)
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Редирект со страниц если пользователь анонимный."""
        login_url = reverse('users:login')
        for name, args in self.urls:
            with self.subTest("Страница не доступна", name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
