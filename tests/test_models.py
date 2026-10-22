import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import db
from models import User, Event, Registration

def test_user_creation_valid(client):
    u = User(username="anna", email="anna@mail.ru", 
             password_hash="x", role="user", is_deaf=True)
    db.session.add(u)
    db.session.commit()
    found = User.query.filter_by(email="anna@mail.ru").first()
    assert found is not None
    assert found.is_deaf is True

def test_user_duplicate_email_fails(client):
    db.session.add(User(username="a", email="dup@mail.ru", password_hash="x"))
    db.session.commit()
    db.session.add(User(username="b", email="dup@mail.ru", password_hash="x"))
    with pytest.raises(Exception):
        db.session.commit()

def test_event_requires_title(client):
    db.session.add(User(username="org", email="org@mail.ru", password_hash="x"))
    db.session.commit()
    org = User.query.filter_by(email="org@mail.ru").first()
    ev = Event(organizer_id=org.id, event_date="2026-11-01 12:00:00")
    db.session.add(ev)
    with pytest.raises(Exception):
        db.session.commit()

def test_registration_unique_per_user_event(client):
    db.session.add(User(username="o", email="o@mail.ru", password_hash="x", role="organizer"))
    db.session.add(User(username="p", email="p@mail.ru", password_hash="x"))
    db.session.commit()
    org = User.query.filter_by(email="o@mail.ru").first()
    part = User.query.filter_by(email="p@mail.ru").first()
    ev = Event(title="Кинопросмотр", organizer_id=org.id, 
               event_date="2026-11-01 12:00:00", is_inclusive=True)
    db.session.add(ev)
    db.session.commit()
    db.session.add(Registration(user_id=part.id, event_id=ev.id, status="pending"))
    db.session.commit()
    db.session.add(Registration(user_id=part.id, event_id=ev.id, status="pending"))
    with pytest.raises(Exception):
        db.session.commit()

def test_event_organizer_relationship(client):
    org = User(username="org2", email="org2@mail.ru", password_hash="x", role="organizer")
    db.session.add(org)
    db.session.commit()
    ev = Event(title="Экскурсия", organizer_id=org.id, event_date="2026-11-02 18:00:00")
    db.session.add(ev)
    db.session.commit()
    found = Event.query.filter_by(title="Экскурсия").first()
    assert found is not None
    assert found.organizer_id == org.id

def test_user_deaf_flag_persisted(client):
    u = User(username="misha", email="misha@mail.ru", password_hash="x", is_deaf=True)
    db.session.add(u)
    db.session.commit()
    found = User.query.filter_by(email="misha@mail.ru").first()
    assert found.is_deaf is True