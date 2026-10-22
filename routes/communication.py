from flask import Blueprint, request, jsonify

from models import db, Event, ChatMessage, Notification, Review
from utils.security import token_required

comm_bp = Blueprint("communication", __name__)


@comm_bp.get("/api/events/<int:event_id>/messages")
def list_messages(event_id):
    Event.query.get_or_404(event_id)
    msgs = (ChatMessage.query.filter_by(event_id=event_id)
            .order_by(ChatMessage.created_at).all())
    return jsonify([{
        "id": m.id,
        "user_id": m.user_id,
        "message": m.message,
        "created_at": m.created_at.isoformat(),
    } for m in msgs]), 200


@comm_bp.post("/api/events/<int:event_id>/messages")
@token_required
def post_message(event_id):
    Event.query.get_or_404(event_id)
    data = request.get_json(silent=True) or {}
    text = (data.get("message") or "").strip()
    if not text:
        return jsonify({"error": "Пустое сообщение"}), 400
    m = ChatMessage(event_id=event_id, user_id=request.user_id, message=text)
    db.session.add(m)
    db.session.commit()
    return jsonify({"message": "Сообщение отправлено", "message_id": m.id}), 201


@comm_bp.get("/api/notifications")
@token_required
def my_notifications():
    notifs = (Notification.query.filter_by(user_id=request.user_id)
              .order_by(Notification.created_at.desc()).all())
    return jsonify([{
        "id": n.id,
        "type": n.type,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
    } for n in notifs]), 200


@comm_bp.post("/api/notifications/read")
@token_required
def mark_read():
    for n in Notification.query.filter_by(
            user_id=request.user_id, is_read=False).all():
        n.is_read = True
    db.session.commit()
    return jsonify({"message": "Уведомления отмечены прочитанными"}), 200


@comm_bp.get("/api/events/<int:event_id>/reviews")
def list_reviews(event_id):
    Event.query.get_or_404(event_id)
    reviews = Review.query.filter_by(event_id=event_id).all()
    return jsonify([{
        "id": r.id,
        "user_id": r.user_id,
        "rating": r.rating,
        "comment": r.comment,
    } for r in reviews]), 200


@comm_bp.post("/api/events/<int:event_id>/reviews")
@token_required
def post_review(event_id):
    Event.query.get_or_404(event_id)
    data = request.get_json(silent=True) or {}
    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({"error": "Оценка — число от 1 до 5"}), 400
    if not 1 <= rating <= 5:
        return jsonify({"error": "Оценка — число от 1 до 5"}), 400
    if Review.query.filter_by(user_id=request.user_id,
                              event_id=event_id).first():
        return jsonify({"error": "Отзыв уже оставлен"}), 400
    r = Review(user_id=request.user_id, event_id=event_id, rating=rating,
               comment=(data.get("comment") or "").strip() or None)
    db.session.add(r)
    db.session.commit()
    return jsonify({"message": "Отзыв сохранён", "review_id": r.id}), 201