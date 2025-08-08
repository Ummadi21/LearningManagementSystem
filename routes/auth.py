from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models import User
from flask_jwt_extended import create_access_token
import random, string
import datetime
from datetime import datetime, timedelta
from utils.email_service import send_otp_email


auth_bp = Blueprint('auth', __name__)

# ---------- REGISTER ----------
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if user already exists
    if existing_user := User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "User already exists"}), 409

    # Hash password
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Create new user
    new_user = User(
        name=data['name'],
        email=data['email'],
        username=data['username'],
        password=hashed_pw,
        role=data['role']  # student, instructor, admin
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"msg": "Invalid username or password"}), 401

    # Create JWT token
    access_token = create_access_token(
        identity={"id": user.id, "username": user.username, "role": user.role},
        expires_delta=datetime.timedelta(hours=1)
    )

    return jsonify({
        "msg": "Login successful",
        "token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "role": user.role
        }
    }), 200
    
# In-memory OTP store (you can replace with DB if needed)
otp_store = {}

# ---------- REQUEST OTP ----------
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "No user found with that email"}), 404

    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }

    sent = send_otp_email(email, otp)
    if not sent:
        return jsonify({"msg": "Failed to send email"}), 500

    return jsonify({"msg": "OTP sent to email"}), 200

# ---------- RESET PASSWORD ----------
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    record = otp_store.get(email)

    if not record or record["otp"] != otp:
        return jsonify({"msg": "Invalid OTP"}), 400

    if datetime.utcnow() > record["expires_at"]:
        return jsonify({"msg": "OTP expired"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_pw
    db.session.commit()

    otp_store.pop(email, None)  # clear used OTP

    return jsonify({"msg": "Password reset successful"}), 200
