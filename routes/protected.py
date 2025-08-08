from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required

protected_bp = Blueprint('protected', __name__)

@protected_bp.route('/admin-only', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_route():
    user = get_jwt_identity()
    return jsonify({"msg": f"Hello Admin {user['username']}"}), 200

@protected_bp.route('/instructor-only', methods=['GET'])
@jwt_required()
@role_required('instructor')
def instructor_route():
    user = get_jwt_identity()
    return jsonify({"msg": f"Hello Instructor {user['username']}"}), 200

@protected_bp.route('/student-only', methods=['GET'])
@jwt_required()
@role_required('student')
def student_route():
    user = get_jwt_identity()
    return jsonify({"msg": f"Hello Student {user['username']}"}), 200