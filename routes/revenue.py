from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import Enrollment, Course
from utils.decorators import role_required
from extensions import db
from sqlalchemy import func
from datetime import datetime

revenue_bp = Blueprint('revenue', __name__)

# ---------- Revenue Summary ----------
@revenue_bp.route('/summary', methods=['GET'])
@jwt_required()
@role_required('admin')
def revenue_summary():
    enrollments = db.session.query(
        Course.name,
        func.count(Enrollment.id).label('total_enrollments'),
        func.sum(Enrollment.payment_amount).label('total_revenue')
    ).join(Course, Enrollment.course_id == Course.id) \
    .group_by(Course.name).all()

    result = []
    for row in enrollments:
        result.append({
            "course_name": row[0],
            "total_enrollments": row[1],
            "total_revenue": float(row[2]) if row[2] else 0.0
        })

    return jsonify(result), 200

# ---------- Revenue Filtered by Date ----------
@revenue_bp.route('/summary-by-date', methods=['POST'])
@jwt_required()
@role_required('admin')
def revenue_by_date():
    data = request.get_json()
    start_date = datetime.strptime(data['start'], '%Y-%m-%d')
    end_date = datetime.strptime(data['end'], '%Y-%m-%d')

    enrollments = db.session.query(
        Course.name,
        func.count(Enrollment.id).label('total_enrollments'),
        func.sum(Enrollment.payment_amount).label('total_revenue')
    ).join(Course, Enrollment.course_id == Course.id) \
    .filter(Enrollment.timestamp >= start_date, Enrollment.timestamp <= end_date) \
    .group_by(Course.name).all()

    result = []
    for row in enrollments:
        result.append({
            "course_name": row[0],
            "total_enrollments": row[1],
            "total_revenue": float(row[2]) if row[2] else 0.0
        })

    return jsonify(result), 200