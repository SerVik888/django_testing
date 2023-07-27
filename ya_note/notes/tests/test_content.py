from django.test import Client, TestCase
from django.urls import reverse

from notes.constance import NOTES_LIST
from notes.forms import NoteForm
from notes.models import Note, User


class TestContent(TestCase):

    NOTES_LIST = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Я')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='i_5',
            author=cls.author
        )

    def test_notes_count(self):
        """Oтдельная заметка передаётся на страницу"""
        response = self.user_client.get(NOTES_LIST)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, 1)

    def test_note_not_in_list_for_another_user(self):
        """Если это не автор заметки, заметка не должна быть ему видна"""
        self.user_client.force_login(self.reader)
        response = self.user_client.get(NOTES_LIST)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, 0)

    def test_authorized_client_has_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for url, args in urls:
            with self.subTest(url=url):
                response = self.user_client.get(reverse(url, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
