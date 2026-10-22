from datetime import datetime

from flask import Blueprint, request, jsonify

from models import db, Event, Registration, Notification
from utils.security import role_required

events_bp = Blueprint("events", __name__)


def event_to_json(e):
    return {
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "event_date": e.event_date.isoformat(),
        "location": e.location,
        "is_inclusive": e.is_inclusive,
        "organizer_id": e.organizer_id,
    }


@events_bp.get("/api/events")
def list_events():
    query = Event.query.filter_by(status="active")
    if request.args.get("inclusive") == "1":
        query = query.filter_by(is_inclusive=True)
    events = query.order_by(Event.event_date).all()
    return jsonify([event_to_json(e) for e in events]), 200


@events_bp.get("/api/events/<int:event_id>")
def get_event(event_id):
    e = Event.query.get_or_404(event_id)
    return jsonify(event_to_json(e)), 200


@events_bp.post("/api/events")
@role_required("organizer", "admin")
def create_event():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    raw_date = data.get("event_date")

    if not title:
        return jsonify({"error": "Укажите название"}), 400
    if not raw_date:
        return jsonify({"error": "Укажите дату и время"}), 400
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({"error": "Формат даты: ГГГГ-ММ-ДД ЧЧ:ММ"}), 400

    event = Event(
        title=title,
        description=data.get("description"),
        event_date=dt,
        location=data.get("location"),
        is_inclusive=bool(data.get("is_inclusive", False)),
        organizer_id=request.user_id,
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Мероприятие создано", "event_id": event.id}), 201


@events_bp.delete("/api/events/<int:event_id>")
@role_required("organizer", "admin")
def cancel_event(event_id):
    e = Event.query.get_or_404(event_id)
    if request.user_role != "admin" and e.organizer_id != request.user_id:
        return jsonify({"error": "Это мероприятие создал другой организатор"}), 403
    e.status = "cancelled"
    for reg in Registration.query.filter_by(
            event_id=event_id, status="pending").all():
        reg.status = "cancelled"
        db.session.add(Notification(
            user_id=reg.user_id,
            event_id=event_id,
            type="cancellation",
            message=f"Мероприятие '{e.title}' отменено организатором",
        ))
    db.session.commit()
    return jsonify({"message": "Мероприятие отменено"}), 200


@events_bp.get("/api/health")
def health():
    return jsonify({"status": "ok"}), 200