import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

load_dotenv()

app = Flask(__name__)

# Безопасная конфигурация с фоллбэком (решает проблему с тестами и запуском без .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-for-tests')

# Импортируем db и модели из models.py
from models import db, User, Event, Registration

db.init_app(app)

with app.app_context():
    db.create_all()

# Декоратор проверки JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Неверный формат токена!"}), 401

        if not token:
            return jsonify({"error": "Токен отсутствует!"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.session.get(User, data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Срок действия токена истек!"}), 401
        except (jwt.InvalidTokenError, AttributeError):
            return jsonify({"error": "Недействительный токен!"}), 401

        return f(current_user, *args, **kwargs)
    return decorated


# ===== API Эндпоинты =====

@app.route('/api', methods=['GET'])
def api_root():
    return {"message": "AccessEvent API is running!"}

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email', username + '@mail.ru' if username else '')
    password = data.get('password')
    role = data.get('role', 'user')

    if not email or '@' not in email or '.' not in email:
        return jsonify({"error": "Некорректный email"}), 400

    if not username or not password:
        return jsonify({"error": "Отсутствуют обязательные поля"}), 400

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"error": "Имя или email уже заняты"}), 400

    new_user = User(username=username, email=email, role=role)
    new_user.password_hash = generate_password_hash(password)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Пользователь успешно зарегистрирован!", "user_id": new_user.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif username:
        user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Неверный логин или пароль"}), 401

    token_payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({"token": token, "role": user.role}), 200

@app.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    result = []
    for event in events:
        result.append({
            "id": event.id,
            "title": event.title,
            "event_date": str(event.event_date),
            "is_inclusive": event.is_inclusive
        })
    return jsonify(result), 200

@app.route('/api/events', methods=['POST'])
@token_required
def create_event(current_user):
    data = request.get_json() or {}
    title = data.get('title')
    event_date = data.get('event_date', '2026-11-01 12:00:00')

    if not title:
        return jsonify({"error": "Поле title обязательно"}), 400

    new_event = Event(
        title=title,
        event_date=event_date,
        organizer_id=current_user.id,
        is_inclusive=data.get('is_inclusive', False)
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({"message": "Мероприятие создано", "event_id": new_event.id}), 201

@app.route('/api/events/<int:event_id>/register', methods=['POST'])
@token_required
def register_for_event(current_user, event_id):
    existing = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing:
        return jsonify({"error": "Уже зарегистрирован"}), 400
    
    reg = Registration(user_id=current_user.id, event_id=event_id, status="pending")
    db.session.add(reg)
    db.session.commit()
    return jsonify({"message": "Успешно зарегистрировано"}), 201

@app.route('/api/my-registrations', methods=['GET'])
@token_required
def my_registrations(current_user):
    regs = Registration.query.filter_by(user_id=current_user.id).all()
    result = [{"id": r.id, "event_id": r.event_id, "status": r.status} for r in regs]
    return jsonify(result), 200


# ===== Фронтенд маршруты =====

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/events-view')
def events_page():
    return render_template('events.html')

@app.route('/login-view', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = (request.form.get('email') or request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        user = User.query.filter_by(username=username).first() or User.query.filter_by(email=username).first()
        if user and user.check_password(password):
            return redirect(url_for('profile_page', user_id=user.id))
        return render_template('login.html', error='Неверный логин или пароль'), 401
    return render_template('login.html')

@app.route('/register-view', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or username + '@mail.ru').strip()
        password = request.form.get('password') or ''
        
        if not username or len(password) < 8:
            return render_template('register.html', error='Проверьте поля: имя обязательно, пароль минимум 8 символов'), 400

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return render_template('register.html', error='Имя пользователя или email уже заняты'), 400

        new_user = User(username=username, email=email, role='user')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_page'))

    return render_template('register.html')

@app.route('/profile/<int:user_id>')
def profile_page(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return 'Пользователь не найден', 404
    return render_template('profile.html', user=user, registrations=[])

if __name__ == '__main__':
    app.run(debug=True, port=5000)