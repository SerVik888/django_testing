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

    def test_pages_availability(self):
        """Доступность страниц анонимному пользователю"""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for url in urls:
            url = reverse(url)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Редирект со страниц если пользователь анонимный."""
        login_url = reverse('users:login')
        urls = (

            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))

        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_note_availability_for_note_edit_delete_and_read(self):
        """Страница не найдена если это не автор заметки"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability_for_an_authenticated_user(self):
        """Авторизованному пользователю доступны страницы со списком заметок,
        страница успешного добавления заметки,
        страница добавления новой заметки
        """
        self.client.force_login(self.author)
        for page in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(page=page):
                response = self.client.get(reverse(page))
                self.assertEqual(response.status_code, HTTPStatus.OK)
