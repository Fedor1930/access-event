# API AccessEvent
 
| Метод | URL | Доступ | Вход (JSON) | Ответы |
|---|---|---|---|---|
| POST | /api/register | гость | username, email, password, role | 201 / 400 |
| POST | /api/login | гость | email, password | 200 token / 401 |
| GET | /api/events | все | - | 200 список |
| GET | /api/events/<id> | все | - | 200 / 404 |
| POST | /api/events | organizer, admin | title, event_date, ... | 201 / 400 / 401 / 403 |
| DELETE | /api/events/<id> | organizer, admin | - | 200 / 403 |
| GET | /api/health | все | - | 200 {"status":"ok"} |
| POST | /api/events/<id>/register | авторизованный | - | 201 / 400 |
| GET | /api/my/registrations | авторизованный | - | 200 |
| PATCH | /api/registrations/<id> | organizer, admin | status | 200 / 400 / 403 |
| GET | /api/notifications | авторизованный | - | 200 |
| POST | /api/notifications/read | авторизованный | - | 200 |
| GET | /api/events/<id>/messages | все | - | 200 |
| POST | /api/events/<id>/messages | авторизованный | message | 201 / 400 |
| GET | /api/events/<id>/reviews | все | - | 200 |
| POST | /api/events/<id>/reviews | авторизованный | rating, comment | 201 / 400 |
 
### Примеры
POST /api/register:
{"username": "anna", "email": "anna@mail.ru", "password": "Passw0rd!", "role": "user"}
Ответ: {"message": "Пользователь создан", "user_id": 1}
 
POST /api/events:
{"title": "Кинопросмотр", "event_date": "2026-12-01 12:00", "is_inclusive": true}
Ответ: {"message": "Мероприятие создано", "event_id": 1}
 
POST /api/events/1/messages:
{"message": "Здравствуйте!"}
Ответ: {"message": "Сообщение отправлено", "message_id": 1}