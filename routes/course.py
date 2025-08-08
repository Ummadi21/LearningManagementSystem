from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Course
from extensions import db
from utils.decorators import role_required
from models import Enrollment
from routes.socket_events import send_course_update

course_bp = Blueprint('course', __name__)

# ---------- CREATE COURSE ----------
@course_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('instructor')
def create_course():
    data = request.get_json()
    new_course = Course(
        name=data['name'],
        description=data.get('description', ''),
        price=data.get('price', 0.0),
        duration=data.get('duration', 'N/A'),
        highlights=data.get('highlights', ''),
        rating=0  # default rating
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"msg": "Course created successfully"}), 201

# ---------- GET ALL COURSES ----------
@course_bp.route('/', methods=['GET'])
@jwt_required()
def get_courses():
    courses = Course.query.all()
    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "price": course.price,
            "duration": course.duration,
            "highlights": course.highlights,
            "rating": course.rating
        })
    return jsonify(result), 200

# ---------- UPDATE COURSE ----------
@course_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
@role_required('instructor')
def update_course(course_id):
    data = request.get_json()
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    course.name = data.get('name', course.name)
    course.description = data.get('description', course.description)
    course.price = data.get('price', course.price)
    course.duration = data.get('duration', course.duration)
    course.highlights = data.get('highlights', course.highlights)

    db.session.commit()
    send_course_update(course.name)
    return jsonify({"msg": "Course updated"}), 200

# ---------- DELETE COURSE ----------
@course_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
@role_required('instructor')
def delete_course(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    db.session.delete(course)
    db.session.commit()
    return jsonify({"msg": "Course deleted"}), 200



# ---------- POPULAR COURSES ----------
@course_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular_courses():
    courses = Course.query.all()
    course_list = []

    for course in courses:
        enrollment_count = Enrollment.query.filter_by(course_id=course.id).count()
        course_list.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "duration": course.duration,
            "price": course.price,
            "rating": course.rating,
            "popularity": enrollment_count
        })

    # Sort by popularity (most enrolled first)
    sorted_courses = sorted(course_list, key=lambda c: c['popularity'], reverse=True)
    return jsonify(sorted_courses), 200