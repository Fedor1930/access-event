# Руководство администратора AccessEvent
 
## Системные требования
Python 3.11+, PostgreSQL 16, Docker (опционально).
 
## Развёртывание
1. docker compose up — приложение на http://localhost:5000.
2. Альтернатива: python app.py с настроенным .env.
 
## Переменные окружения (.env)
| Переменная | Назначение |
|---|---|
| SECRET_KEY | подпись JWT-токенов |
| DATABASE_URL | строка подключения к PostgreSQL |
 
## Роли и права
См. docs/security.md (таблица ролей с наследованием).
 
## Резервное копирование
pg_dump -U postgres accessevent > backup.sql
Восстановление: psql -U postgres accessevent < backup.sql
 
## Типовые проблемы
1. Порт 5000 занят — остановить предыдущий процесс.
2. connection refused — служба PostgreSQL не запущена (services.msc).
3. password authentication failed — пароль в .env не совпадает с БД.
4. Контейнер не видит базу — проверьте db:5432 в DATABASE_URL.
5. Тесты стёрли данные — запускались без TESTING=1 (в эталоне исправлено).