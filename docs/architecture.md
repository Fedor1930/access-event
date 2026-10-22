# Архитектура AccessEvent
 
## 1. Трёхслойная архитектура
 
| Слой | Технологии | Ответственность |
|---|---|---|
| Клиентский (Frontend) | HTML, CSS, JS, Jinja2 | Отображение, ввод, визуальные уведомления, чат |
| Серверный (Backend) | Python 3.11, Flask, SQLAlchemy | Бизнес-логика, REST API, JWT, роли |
| Данные | PostgreSQL 16 | Хранение, целостность через FK и CHECK |
 
## 2. Паттерн MVC
 
| Часть MVC | Реализация | Файлы |
|---|---|---|
| Model | SQLAlchemy-модели | models.py |
| View | Jinja2-шаблоны | templates/*.html |
| Controller | Маршруты Flask | routes/*.py |
 
## 3. Схема взаимодействия клиент-сервер
Браузер -> HTTP -> Flask (маршруты) -> ORM (SQLAlchemy) -> PostgreSQL
Браузер <- HTML+JSON <- Flask <- объекты Python <- SQLAlchemy
 
## 4. Список API-эндпоинтов
 
| Метод | URL | Доступ | Назначение |
|---|---|---|---|
| POST | /api/register | гость | регистрация |
| POST | /api/login | гость | вход, выдача JWT |
| GET | /api/events | все | список активных мероприятий |
| GET | /api/events/<id> | все | карточка мероприятия |
| POST | /api/events | organizer, admin | создание мероприятия |
| DELETE | /api/events/<id> | organizer, admin | отмена мероприятия |
| GET | /api/health | все | проверка живости |
| POST | /api/events/<id>/register | авторизованный | регистрация на мероприятие |
| GET | /api/my/registrations | авторизованный | свои регистрации |
| PATCH | /api/registrations/<id> | organizer, admin | подтверждение заявки |
| GET | /api/notifications | авторизованный | свои уведомления |
| POST | /api/notifications/read | авторизованный | отметить прочитанными |
| GET | /api/events/<id>/messages | все | сообщения чата |
| POST | /api/events/<id>/messages | авторизованный | отправить сообщение |
| GET | /api/events/<id>/reviews | все | отзывы |
| POST | /api/events/<id>/reviews | авторизованный | оставить отзыв |
 
## 5. Инклюзивность по слоям
- Frontend: ARIA-атрибуты, контраст 4.5:1, skip-link, цветовые статусы с текстом;
- Backend: поле is_deaf в профиле, уведомления и чат в API;
- Данные: таблицы notifications и chat_messages.