from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

LOGIN_URL = reverse("users:login")


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),

    )
)
def test_availability_for_anonymous_user(client, name, args):
    """Анонимный пользователь может попасть на главную страинцу, страницы
    регистрации, входа в учётную запись и выхода из неё
    """
    response = client.get(reverse(name, args=args))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('auth_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('another_author'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_availability_pages_edit_delete_for_author_and_reader(
    parametrized_client, expected_status, comment, name
):
    """Зарегестрированный пользователь может редактировать или удалять
    свои комментарии, но не может чужие.
    """
    response = parametrized_client.get(reverse(name, args=(comment.pk,)))
    assert response.status_code == expected_status


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
