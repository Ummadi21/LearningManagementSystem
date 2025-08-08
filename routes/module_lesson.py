from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils.decorators import role_required
from models import Module, Lesson, Course
from  extensions import db

ml_bp = Blueprint('module_lesson', __name__)

# ---------- Add Module to Course ----------
@ml_bp.route('/modules/<int:course_id>', methods=['POST'])
@jwt_required()
@role_required('instructor')
def create_module(course_id):
    data = request.get_json()
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    module = Module(title=data['title'], course_id=course_id)
    db.session.add(module)
    db.session.commit()
    return jsonify({"msg": "Module added"}), 201

# ---------- Add Lesson to Module ----------
@ml_bp.route('/lessons/<int:module_id>', methods=['POST'])
@jwt_required()
@role_required('instructor')
def create_lesson(module_id):
    data = request.get_json()
    module = Module.query.get(module_id)
    if not module:
        return jsonify({"msg": "Module not found"}), 404

    lesson = Lesson(
        title=data['title'],
        content=data.get('content', ''),
        module_id=module_id
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify({"msg": "Lesson added"}), 201

# ---------- Get Modules & Lessons by Course ----------
@ml_bp.route('/course-structure/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_structure(course_id):
    modules = Module.query.filter_by(course_id=course_id).all()
    result = []
    for mod in modules:
        lessons = Lesson.query.filter_by(module_id=mod.id).all()
        result.append({
            "module_id": mod.id,
            "module_title": mod.title,
            "lessons": [
                {"lesson_id": l.id, "title": l.title, "content": l.content} for l in lessons
            ]
        })
    return jsonify(result), 200