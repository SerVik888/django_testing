from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, comment_data):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(reverse('news:detail', args=(news.id,)), data=comment_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(auth_client, news, comment_data):
    """Авторизованный пользователь может отправить комментарий."""
    auth_client.post(
        reverse('news:detail', args=(news.id,)), data=comment_data
    )
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_user_cant_use_bad_words(auth_client, news):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
      а форма вернёт ошибку.
      """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = auth_client.post(
        reverse('news:detail', args=(news.id,)), data=bad_words_data
    )
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(auth_client, news, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = auth_client.delete(reverse('news:delete', args=(comment.pk,)))
    assertRedirects(
        response, reverse('news:detail', args=(news.id,)) + '#comments'
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(auth_client, news, comment_data, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = auth_client.post(
        reverse('news:edit', args=(comment.pk,)), data=comment_data
    )
    assertRedirects(
        response, reverse('news:detail', args=(news.id,)) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == comment_data['text']


def test_user_cant_edit_comment_of_another_user(
        another_author, comment_data, comment
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = another_author.post(
        reverse('news:edit', args=(comment.pk,)), data=comment_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != comment_data['text']


def test_user_cant_delete_comment_of_another_user(
        another_author, comment_data, comment
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = another_author.delete(
        reverse('news:delete', args=(comment.pk,)), data=comment_data
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
