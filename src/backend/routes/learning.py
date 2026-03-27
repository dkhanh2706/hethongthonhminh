from flask import Blueprint, request, jsonify
from models.model import (
    recommend_question,
    get_adaptive_recommendations,
    submit_answer,
    get_dashboard,
    get_analysis,
    get_question_bank
)

learning_bp = Blueprint('learning', __name__)


@learning_bp.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    score = float(data.get("score", 0))
    time = float(data.get("time", 0))
    result = recommend_question(score, time)
    return jsonify(result)


@learning_bp.route('/recommend/adaptive', methods=['POST'])
def adaptive_recommend():
    data = request.json
    username = data.get("username", "").strip()
    count = int(data.get("count", 5))

    if not username:
        return jsonify({"success": False, "message": "Thiếu tên người dùng"}), 400

    result = get_adaptive_recommendations(username, count)
    return jsonify({"success": True, "data": result})


@learning_bp.route('/learning/submit', methods=['POST'])
def submit():
    data = request.json
    username = data.get("username", "").strip()
    topic = data.get("topic", "").strip()
    subtopic = data.get("subtopic", "").strip()
    question_id = data.get("question_id", "").strip()
    score = float(data.get("score", 0))
    time_spent = float(data.get("time_spent", 0))
    is_correct = bool(data.get("is_correct", False))

    if not username or not question_id:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    result = submit_answer(username, topic, subtopic, question_id, score, time_spent, is_correct)
    return jsonify(result)


@learning_bp.route('/learning/dashboard', methods=['POST'])
def dashboard():
    data = request.json
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "Thiếu tên người dùng"}), 400

    result = get_dashboard(username)
    return jsonify({"success": True, "data": result})


@learning_bp.route('/learning/analysis', methods=['POST'])
def analysis():
    data = request.json
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "Thiếu tên người dùng"}), 400

    result = get_analysis(username)
    return jsonify({"success": True, "data": result})


@learning_bp.route('/learning/question-bank', methods=['GET'])
def question_bank():
    result = get_question_bank()
    return jsonify({"success": True, "data": result})
