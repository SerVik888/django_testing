from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.constance import NOTES_SUCCESS
from notes.forms import WARNING
from notes.models import Note, User


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Я')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.reader)
        cls.first_note = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'i_5',
            'author': cls.author,
        }
        cls.second_note = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'i_6',
        }
        cls.note = cls.user_client.post(
            reverse('notes:add'), data=cls.first_note
        )
        cls.edit_note_url = reverse(
            'notes:edit', args=(cls.first_note['slug'],)
        )
        cls.start_notes_count = Note.objects.count()

    def add_post(self, note_data):
        return self.user_client.post(
            reverse('notes:add'), data=note_data
        )

    def assert_note(self, note_data):
        note = Note.objects.get(slug=note_data['slug'])
        self.assertEqual(note.title, note_data['title'])
        self.assertEqual(note.text, note_data['text'])
        self.assertEqual(note.slug, note_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.assertRedirects(
            self.add_post(self.second_note), NOTES_SUCCESS
        )
        self.assertEqual(Note.objects.count(), self.start_notes_count + 1)
        self.assert_note(self.second_note)

    def test_anonymous_user_cant_create_note(self):
        """Aнонимный пользователь не может создать заметку."""
        url = reverse('notes:add')
        response = self.client.post(url, data=self.second_note)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertEqual(Note.objects.count(), self.start_notes_count)

    def test_not_unique_slug(self):
        """Возможность создать две заметки с одинаковым slug"""
        add_post = self.add_post(self.first_note)
        slug = Note.objects.last().slug
        self.assertFormError(
            add_post, 'form', 'slug', errors=(slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.start_notes_count)

    def test_empty_slug(self):
        """Eсли при создании заметки оставить поле slug пустым"""
        self.second_note.pop('slug')
        self.assertRedirects(self.add_post(self.second_note), NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.start_notes_count + 1)
        new_note = Note.objects.last()
        expected_slug = slugify(self.second_note['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свои заметки"""
        response = self.user_client.post(self.edit_note_url, self.second_note)
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assert_note(self.second_note)

    def test_other_user_cant_edit_note(self):
        """Зарегестрированный пользователь
        не может редактировать чужую заметку.
        """
        response = self.other_client.post(self.edit_note_url, self.first_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assert_note(self.first_note)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.user_client.post(
            reverse('notes:delete', args=(self.first_note['slug'],))
        )
        self.assertRedirects(response, NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.start_notes_count - 1)

    def test_other_user_cant_delete_note(self):
        """Зарегестрированный пользователь не может удалить чужую заметку."""
        url = reverse('notes:delete', args=(Note.objects.last().slug,))
        response = self.other_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.start_notes_count)
