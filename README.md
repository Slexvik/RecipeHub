# Место обмена рецептами RecipeHub
 

## Оглавление
- [Технологии](#используемые-технологии)
- [Описание проекта](#описание-проекта)
- [Запуск проекта](#запуск-проекта)
<br>

## Используемые технологии

:snake: Python 3.9, :desktop_computer: Django 3.2, :arrows_counterclockwise: Django Rest Framework 3.14.0, 

:ship: Docker 3, :paintbrush: Nginx 1.19, :books: Postgres 13.10
<hr>

## Описание проекта
Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации понравившихся авторов.

Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
<hr>


## Запуск проекта
### Для запуска проекта на локальной машине
Необходимо установить Docker на свою рабочую машину. Инструкцию можно найти на [оффициальном сайте](https://docs.docker.com/get-docker/) по Docker.

После установки Docker необходимо:

1. Клонировать репозиторий:
```bash
git clone git@github.com:Slexvik/foodgram-project-react.git
```

2. Перейти в директорию `infra/`:
```bash
cd infra/
```

3. Создать `.env` файл и заполнить его в соответствии с `env.example`.

```bash
touch .env
```

4. В терминали запустить **docker-compose**
```
docker compose up -d
```

5. Выполнить миграции, сборку статических файлов, заполнение базы исходными ингредиентами, создание супер пользователя:
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py load_data
docker-compose exec backend python manage.py load_tags
docker-compose exec backend python manage.py createsuperuser
```
