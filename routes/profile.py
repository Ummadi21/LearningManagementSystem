from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, bcrypt
from models import User

profile_bp = Blueprint('profile', __name__)

# View profile
@profile_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity['username']).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "role": user.role
    }), 200

# Update profile
@profile_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity['username']).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.password = hashed_pw

    db.session.commit()
    return jsonify({"msg": "Profile updated successfully"}), 200