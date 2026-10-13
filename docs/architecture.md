# Архитектура системы AccessEvent

## 1. Трёхслойная архитектура

### Клиентский слой (Frontend)
- **Технологии:** HTML5, CSS3, JavaScript, Jinja2
- **Компоненты:** страницы событий, профиль, чат, визуальные уведомления[cite: 6]
- **Адаптация для глухих пользователей:** цветовая индикация вместо звука[cite: 6]

### Серверный слой (Backend)
- **Технологии:** Python 3.11+, Flask, SQLAlchemy[cite: 6]
- **Компоненты:** маршрутизация, бизнес-логика, ORM, подсистема безопасности[cite: 6]
- **Паттерн:** MVC (Model-View-Controller)[cite: 6]

### Слой данных
- **СУБД:** PostgreSQL 15[cite: 6]
- **Таблицы:** users, events, registrations, messages, event_categories, event_category_link, notifications[cite: 6]

## 2. Клиент-серверное взаимодействие
- `GET /events` — список мероприятий[cite: 6]
- `POST /events` — создание мероприятия[cite: 6]
- `PUT /events/{id}` — обновление[cite: 6]
- `DELETE /events/{id}` — удаление[cite: 6]

## 3. Инфраструктура
- **GitHub Actions** — автоматизированная проверка (CI/CD)[cite: 6]
- **Docker** — контейнеризация[cite: 6]
- **GHCR** — реестр Docker-образов[cite: 6]
