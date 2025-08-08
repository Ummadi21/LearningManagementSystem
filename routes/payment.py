import razorpay
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Course, User, Enrollment
from utils.decorators import role_required
import os

payment_bp = Blueprint('payment', __name__)

# Razorpay client
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

# ---------- Create Payment Order ----------
@payment_bp.route('/create-order/<int:course_id>', methods=['POST'])
@jwt_required()
@role_required('student')
def create_order(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    # Amount in paise (INR)
    amount = int(course.price * 100)

    order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify({
        "order_id": order["id"],
        "currency": order["currency"],
        "amount": order["amount"],
        "key_id": os.getenv("RAZORPAY_KEY_ID"),
        "course": {
            "id": course.id,
            "name": course.name,
            "price": course.price
        }
    }), 200

# ---------- Verify Payment & Enroll ----------
@payment_bp.route('/verify-payment', methods=['POST'])
@jwt_required()
@role_required('student')
def verify_payment():
    data = request.get_json()
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity['username']).first()

    try:
        # Verify signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
    except:
        return jsonify({"msg": "Invalid payment signature"}), 400

    # Enroll student in course
    course_id = data['course_id']
    existing = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing:
        return jsonify({"msg": "Already enrolled"}), 400

    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"msg": "Payment successful. Enrolled!"}), 200