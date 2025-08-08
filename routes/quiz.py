from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import QuizQuestion, QuizSubmission, Module, User
from utils.decorators import role_required

quiz_bp = Blueprint('quiz', __name__)

# ---------- Instructor Adds a Quiz Question ----------
@quiz_bp.route('/question/<int:module_id>', methods=['POST'])
@jwt_required()
@role_required('instructor')
def add_question(module_id):
    data = request.get_json()
    question = QuizQuestion(
        module_id=module_id,
        question_text=data['question_text'],
        options=data['options'],  # e.g. { "a": "Option 1", "b": "Option 2", ... }
        correct_answer=data['correct_answer']  # one of: a, b, c, d
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({"msg": "Question added"}), 201

# ---------- Student Submits Quiz ----------
@quiz_bp.route('/submit/<int:module_id>', methods=['POST'])
@jwt_required()
@role_required('student')
def submit_quiz(module_id):
    data = request.get_json()
    answers = data.get('answers')  # { question_id: "a", question_id2: "b" }

    total = len(answers)
    correct = 0

    for qid, submitted_answer in answers.items():
        question = QuizQuestion.query.get(int(qid))
        if question and question.correct_answer.lower() == submitted_answer.lower():
            correct += 1

    score = (correct / total) * 100 if total else 0

    identity = get_jwt_identity()
    user = User.query.filter_by(username=identity['username']).first()

    submission = QuizSubmission(user_id=user.id, module_id=module_id, score=score)
    db.session.add(submission)
    db.session.commit()

    return jsonify({"msg": "Quiz submitted", "score": score}), 200

# ---------- View All Questions in a Module ----------
@quiz_bp.route('/questions/<int:module_id>', methods=['GET'])
@jwt_required()
def get_questions(module_id):
    from models import QuizQuestion, QuizSubmission, Module, User
    questions = QuizQuestion.query.filter_by(module_id=module_id).all()
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "question_text": q.question_text,
            "options": q.options
        })
    return jsonify(result), 200