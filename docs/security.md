# Подсистема безопасности AccessEvent

## 1. Аутентификация
### Регистрация
- Пользователь указывает: username, email, password
- Пароль хешируется через Werkzeug (pbkdf2:sha256)
- Хранится только password_hash, пароль в открытом виде не сохраняется

### Вход (login)
- Пользователь вводит email и пароль
- Сервер проверяет хеш через check_password_hash()
- При успехе генерируется JWT-токен (access token, срок 1 час)
- Выдаётся refresh token (срок 30 дней)[cite: 6]

### Проверка токена
- Каждый запрос: заголовок Authorization: Bearer <token>[cite: 6]
- Сервер декодирует JWT, проверяет подпись и срок действия[cite: 6]
- При истечении access token — обновление через refresh token[cite: 6]

## 2. Хеширование паролей
- Метод: pbkdf2:sha256 (Werkzeug)[cite: 6]
- Пример: generate_password_hash("pass123", method='pbkdf2:sha256')[cite: 6]
- Проверка: check_password_hash(stored_hash, "pass123")[cite: 6]

## 3. Авторизация (RBAC)
### Роли
| Роль | Права |
|------|-------|
| guest | Просмотр событий и категорий[cite: 6] |
| user | Регистрация на события, чат, уведомления, профиль[cite: 6] |
| organizer | Создание и управление событиями (все права user)[cite: 6] |
| admin | Управление пользователями, модерация (все права organizer)[cite: 6] |

### Наследование прав
guest -> user -> organizer -> admin[cite: 6]

### Реализация
- Декоратор @role_required(*roles) проверяет роль из JWT[cite: 6]
- При недостатке прав — HTTP 403 Forbidden[cite: 6]

## 4. JWT (JSON Web Token)
- Header: {"alg": "HS256", "typ": "JWT"}[cite: 6]
- Payload: {"user_id": 1, "role": "organizer", "exp": 1700000000}[cite: 6]
- Signature: HMAC-SHA256 с секретным ключом приложения[cite: 6]

## 5. Инклюзивные функции безопасности
- Поле is_deaf в таблице users — адаптация интерфейса[cite: 6]
- Визуальные уведомления (таблица notifications) вместо звуковых[cite: 6]
- Текстовый чат (таблица messages) вместо голосового общения[cite: 6]
- Цветовая индикация статусов (pending=жёлтый, confirmed=зелёный, cancelled=красный)[cite: 6]
