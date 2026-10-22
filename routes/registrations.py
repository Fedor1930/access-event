from flask import Blueprint, request, jsonify

from models import db, Event, Registration, Notification
from utils.security import token_required, role_required

reg_bp = Blueprint("registrations", __name__)


@reg_bp.post("/api/events/<int:event_id>/register")
@token_required
def register_on_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.status != "active":
        return jsonify({"error": "Мероприятие не активно"}), 400
    existing = Registration.query.filter_by(
        user_id=request.user_id, event_id=event_id).first()
    if existing:
        return jsonify({"error": "Вы уже зарегистрированы"}), 400

    reg = Registration(user_id=request.user_id, event_id=event_id,
                       status="pending")
    db.session.add(reg)
    db.session.add(Notification(
        user_id=event.organizer_id,
        event_id=event_id,
        type="info",
        message=f"Новая заявка на мероприятие '{event.title}'",
    ))
    db.session.commit()
    return jsonify({
        "message": "Регистрация создана",
        "registration_id": reg.id,
        "status": reg.status,
    }), 201


@reg_bp.get("/api/my/registrations")
@token_required
def my_registrations():
    regs = (Registration.query.filter_by(user_id=request.user_id)
            .order_by(Registration.created_at).all())
    return jsonify([{
        "id": r.id,
        "event_id": r.event_id,
        "status": r.status,
        "created_at": r.created_at.isoformat(),
    } for r in regs]), 200


@reg_bp.patch("/api/registrations/<int:reg_id>")
@role_required("organizer", "admin")
def change_status(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    event = Event.query.get_or_404(reg.event_id)
    if request.user_role != "admin" and event.organizer_id != request.user_id:
        return jsonify({"error": "Это мероприятие создал другой организатор"}), 403

    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("confirmed", "cancelled"):
        return jsonify({"error": "Допустимы статусы confirmed и cancelled"}), 400

    reg.status = status
    if status == "confirmed":
        db.session.add(Notification(
            user_id=reg.user_id,
            event_id=reg.event_id,
            type="reminder",
            message=f"Ваша заявка на '{event.title}' подтверждена",
        ))
    db.session.commit()
    return jsonify({"message": "Статус обновлён", "status": reg.status}), 200