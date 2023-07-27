from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

LOGIN_URL = reverse("users:login")


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_availability_for_anonymous_user(client, name):
    """Анонимный пользователь может попасть на главную страинцу, страницы
    регистрации, входа в учётную запись и выхода из неё
    """
    response = client.get(reverse(name))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, detail_url):
    """Анонимный пользователь может попасть на страницу отдельной новости"""
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_pages_availability_for_author(auth_client, comment, name):
    """Автору комментария доступно его изменение и удаление комментария"""
    response = auth_client.get(reverse(name, args=(comment.pk,)))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_pages_edit_delete_for_anonymous_user(
    client, comment, name
):
    """Анoнимному пользователю не доступно редактирование и удаление
    комментариев он должен перенаправляться на страницу авторизации
    """
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{LOGIN_URL}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_pages_edit_delete_for_another_user(
    admin_client, comment, name
):
    """Зарегестрированный пользователю не может редактировать или удалять чужие
    комментарии.
    """
    response = admin_client.get(reverse(name, args=(comment.pk,)))
    assert response.status_code == HTTPStatus.NOT_FOUND
