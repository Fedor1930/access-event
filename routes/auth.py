import re

from flask import Blueprint, request, jsonify

from models import db, User
from utils.security import create_token

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


@auth_bp.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = data.get("role") or "user"

    if not username or not email or not password:
        return jsonify({"error": "Заполните все поля"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Некорректный email"}), 400
    if len(password) < 8:
        return jsonify({"error": "Пароль должен быть от 8 символов"}), 400
    if role not in ("user", "organizer"):
        return jsonify({"error": "Недопустимая роль"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email уже занят"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Имя пользователя уже занято"}), 400

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Пользователь создан", "user_id": user.id}), 201


@auth_bp.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Неверный email или пароль"}), 401

    return jsonify({"token": create_token(user), "role": user.role}), 200