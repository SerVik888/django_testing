from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note, User

# ??? Как убрать дублирование кода на этой странице ???
# ??? Нужно ли здесь убирать одноразовые переменные ???


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Я')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.user_client = Client()
        cls.user_client.force_login(cls.author)
        cls.note_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'i_5',
        }

    def add_post(self):
        return self.user_client.post(
            reverse('notes:add'), data=self.note_data
        )

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        self.assertRedirects(self.add_post(), reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.note_data['title'])
        self.assertEqual(new_note.text, self.note_data['text'])
        self.assertEqual(new_note.slug, self.note_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Aнонимный пользователь не может создать заметку."""
        url = reverse('notes:add')
        response = self.client.post(url, data=self.note_data)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        """Возможность создать две заметки с одинаковым slug"""
        self.add_post()
        slug = Note.objects.get().slug
        self.assertFormError(
            self.add_post(), 'form', 'slug', errors=(slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Eсли при создании заметки оставить поле slug пустым"""
        self.note_data.pop('slug')
        self.assertRedirects(self.add_post(), reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.note_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свои заметки"""
        self.user_client.post(reverse('notes:add'), data=self.note_data)
        url = reverse('notes:edit', args=(Note.objects.get().slug,))
        response = self.user_client.post(url, self.note_data)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get()
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])
        self.assertEqual(note.slug, self.note_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Зарегестрированный пользователь
        не может редактировать чужую заметку.
        """
        self.add_post()
        self.user_client.force_login(self.reader)
        url = reverse('notes:edit', args=(Note.objects.get().slug,))
        response = self.user_client.post(url, self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(slug=self.note_data['slug'])
        self.assertEqual(self.note_data['title'], note_from_db.title)
        self.assertEqual(self.note_data['text'], note_from_db.text)
        self.assertEqual(self.note_data['slug'], note_from_db.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        self.add_post()
        url = reverse('notes:delete', args=(Note.objects.get().slug,))
        response = self.user_client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Зарегестрированный пользователь не может удалить чужую заметку."""
        self.user_client.post(reverse('notes:add'), data=self.note_data)
        self.user_client.force_login(self.reader)
        url = reverse('notes:delete', args=(Note.objects.get().slug,))
        response = self.user_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
