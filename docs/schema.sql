-- AccessEvent: DDL-скрипт (PostgreSQL 16)
-- Внимание: приложение создаёт таблицы через db.create_all() по моделям.
-- Этот файл — проект базы: по нему сверяют модели и ER-диаграмму.
 
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'user',
    is_deaf       BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT ck_users_role CHECK (role IN ('guest', 'user', 'organizer', 'admin'))
);
 
CREATE TABLE categories (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
 
CREATE TABLE events (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(100) NOT NULL,
    description  TEXT,
    event_date   TIMESTAMP    NOT NULL,
    location     VARCHAR(200),
    is_inclusive BOOLEAN      NOT NULL DEFAULT FALSE,
    status       VARCHAR(20)  NOT NULL DEFAULT 'active',
    organizer_id INTEGER      NOT NULL,
    created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_events_status CHECK (status IN ('active', 'cancelled')),
    CONSTRAINT fk_events_organizer FOREIGN KEY (organizer_id)
        REFERENCES users (id) ON DELETE CASCADE
);
 
CREATE TABLE event_categories (
    event_id    INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (event_id, category_id),
    CONSTRAINT fk_ec_event FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE CASCADE,
    CONSTRAINT fk_ec_category FOREIGN KEY (category_id)
        REFERENCES categories (id) ON DELETE CASCADE
);
 
CREATE TABLE registrations (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER     NOT NULL,
    event_id   INTEGER     NOT NULL,
    status     VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_reg_user_event UNIQUE (user_id, event_id),
    CONSTRAINT ck_reg_status CHECK (status IN ('pending', 'confirmed', 'cancelled')),
    CONSTRAINT fk_reg_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_reg_event FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE CASCADE
);
 
CREATE TABLE notifications (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER     NOT NULL,
    event_id   INTEGER,
    type       VARCHAR(20) NOT NULL DEFAULT 'info',
    message    TEXT        NOT NULL,
    is_read    BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_notif_type CHECK (type IN ('info', 'reminder', 'cancellation')),
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_event FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE SET NULL
);
 
CREATE TABLE reviews (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    rating   INTEGER NOT NULL,
    comment  TEXT,
    CONSTRAINT ck_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT uq_review_user_event UNIQUE (user_id, event_id),
    CONSTRAINT fk_rev_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_rev_event FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE CASCADE
);
 
CREATE TABLE chat_messages (
    id         SERIAL PRIMARY KEY,
    event_id   INTEGER   NOT NULL,
    user_id    INTEGER   NOT NULL,
    message    TEXT      NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_event FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE
);
 
CREATE INDEX idx_events_date ON events (event_date);
CREATE INDEX idx_registrations_user ON registrations (user_id, event_id);
CREATE INDEX idx_notifications_user ON notifications (user_id, is_read);
CREATE INDEX idx_chat_event ON chat_messages (event_id);