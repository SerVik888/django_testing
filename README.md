# Проект Django testing

### Краткое описание проекта:
В этом проекте написаны тесты для двух приложений ya_news(pytest) и ya_note(unittest)\
ya_note - сервис для создания заметок\
ya_news - сервис для просмотра новостей
- Тестирование маршрутов
- Тестирование контента
- Тестирование логики приложения


### Как запустить проекты:
`git clone git@github.com:SerVik888/django_testing.git` -> клонировать репозиторий

* Если у вас Linux/macOS\
    `python3 -m venv env` -> создать виртуальное окружение\
    `source env/bin/activate` -> активировать виртуальное окружение\
    `python3 -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    python manage.py loaddata db.json 
    `cd ya_news` или `cd ya_note` -> переходим в папку 
    `python3 manage.py migrate` -> выполнить миграции\
    `python3 manage.py loaddata news/fixtures/news.json` загрузка данных из файла в БД(только для проекта ya_news)\
    `python3 manage.py createsuperuser` -> создать суперпользователя\
    `python3 manage.py runserver` -> запустить проект

* Если у вас windows\
    `python -m venv venv` -> создать виртуальное окружение\
    `source venv/Scripts/activate` -> активировать виртуальное окружение\
    `python -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `cd ya_news` или `cd ya_note` -> переходим в папку 
    `python manage.py migrate` -> выполнить миграции\
    `python manage.py loaddata news/fixtures/news.json` загрузка данных из файла в БД(только для проекта ya_news)\
    `python manage.py createsuperuser` -> создать суперпользователя\
    `python manage.py runserver` -> запустить проект
* После запуска, проект будет доступен по адресу http://127.0.0.1:8000/
* Панель администратора находиться по адресу http://127.0.0.1:8000/admin/

### Как тестировать проекты:
`source venv/Scripts/activate` -> активировать виртуальное окружение\
`cd ya_news` или `cd ya_note` -> переходим в папку 
`pytest` -> Выполнить команду из этой папки(смотря для какого приложения нужно выполнить тесты).

### Как тестировать тесты:
`source venv/Scripts/activate` -> активировать виртуальное окружение\
`run_tests.sh` -> Выполнить команду из корня проекта

### Cписок используемых технологий:
- Django
- pytest
- unittest

Автор: Сафонов Сергей\
Почта: [sergey_safonov86@inbox.ru](mailto:sergey_safonov86@inbox.ru)