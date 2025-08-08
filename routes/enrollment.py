from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Enrollment, Course, User
from utils.decorators import role_required
from utils.email_service import send_email
from utils.sms_service import send_sms

enroll_bp = Blueprint('enroll', __name__)

# ---------- Student Enroll Themselves ----------
@enroll_bp.route('/enroll/<int:course_id>', methods=['POST'])
@jwt_required()
@role_required('student')
def student_enroll(course_id):
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity['username']).first()
    course = Course.query.get(course_id)

    if not course:
        return jsonify({"msg": "Course not found"}), 404

    existing = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing:
        return jsonify({"msg": "Already enrolled"}), 400

    enrollment = Enrollment(user_id=user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"msg": f"Enrolled in course: {course.name}"}), 201

# ---------- Instructor Enrolls a Student ----------
@enroll_bp.route('/enroll/<int:course_id>/<int:student_id>', methods=['POST'])
@jwt_required()
@role_required('instructor')
def instructor_enroll(course_id, student_id):
    student = User.query.get(student_id)
    course = Course.query.get(course_id)

    if not student or student.role != 'student':
        return jsonify({"msg": "Student not found"}), 404

    if not course:
        return jsonify({"msg": "Course not found"}), 404

    existing = Enrollment.query.filter_by(user_id=student.id, course_id=course.id).first()
    if existing:
        return jsonify({"msg": "Student already enrolled"}), 400

    enrollment = Enrollment(user_id=student.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"msg": f"{student.name} enrolled in {course.name}"}), 201

# ---------- View My Enrollments ----------
@enroll_bp.route('/my-enrollments', methods=['GET'])
@jwt_required()
def my_enrollments():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity['username']).first()
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()

    result = []
    for e in enrollments:
        course = Course.query.get(e.course_id)
        result.append({
            "course_id": course.id,
            "course_name": course.name,
            "description": course.description,
            "duration": course.duration
        })

    return jsonify(result), 200
# Inside student_enroll() after db.session.commit():
send_email(
    to_email=User.email,
    subject="Course Enrollment Confirmation",
    html_message=f"<p>You have successfully enrolled in <b>{Course.name}</b>.</p>"
)

# Inside student_enroll() after db.session.commit():
send_email(
    to_email=User.email,
    subject="Course Enrollment Confirmation",
    html_message=f"<p>You have successfully enrolled in <b>{Course.name}</b>.</p>"
)