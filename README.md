# Foodgram — продуктовый помощник

Foodgram — веб-приложение для публикации рецептов. Пользователи могут создавать рецепты, добавлять их в избранное, формировать список покупок и подписываться на других авторов. Проект состоит из бэкенда (Django REST API) и фронтенда (React SPA), упакованных в Docker-контейнеры.

## Стек технологий

- **Backend:** Python 3.12, Django 6.0, Django REST Framework, Djoser (авторизация по токенам)
- **Frontend:** React (SPA), статика раздаётся через Nginx
- **База данных:** PostgreSQL 16
- **Инфраструктура:** Docker, Docker Compose, Nginx, Gunicorn
- **CI/CD:** GitHub Actions (автоматический деплой на сервер)

## Локальный запуск в Docker

1. Убедитесь, что у вас установлены Docker и Docker Compose (версия 2.x).
2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-аккаунт/foodgram.git
   cd foodgram/infra
   docker compose -f docker-compose.yml up -d

Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.
По адресу http://localhost:8080 изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

## Регистрация пользователя

POST /api/users/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "user",
  "first_name": "Иван",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
### Ответ
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Qwerty123"
}

## Получение токена
POST /api/auth/token/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "Qwerty123"
}
### Ответ
{
  "auth_token": "токен..."
}


## Создание рецепта
POST /api/recipes/
Authorization: Token <токен>
Content-Type: application/json

{
  "ingredients": [{"id": 1, "amount": 100}],
  "tags": [1, 2],
  "image": "data:image/png;base64,...",
  "name": "Суп",
  "text": "Варить 10 минут",
  "cooking_time": 10
}

