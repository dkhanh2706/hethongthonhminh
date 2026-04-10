from flask import Blueprint, request, jsonify
from models.model import (
    recommend_question,
    get_adaptive_recommendations,
    submit_answer,
    get_dashboard,
    get_analysis,
    get_question_bank,
    get_weekly_statistics
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


@learning_bp.route('/statistics/weekly', methods=['POST'])
def weekly_statistics():
    result = get_weekly_statistics()
    return jsonify(result)


@learning_bp.route('/statistics/user-average', methods=['POST'])
def user_average_statistics():
    import json
    import os

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    history_file = os.path.join(data_dir, 'quiz_history.json')

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
    except:
        history_data = {}

    user_stats = []
    for username, sessions in history_data.items():
        if not sessions or len(sessions) == 0:
            continue

        total_score = 0
        total_correct = 0
        total_questions = 0
        total_time = 0
        quiz_count = len(sessions)

        for session in sessions:
            score = session.get('score', 0)
            correct = session.get('correct_count', 0)
            total = session.get('total', 0)
            time = session.get('study_time', 0)

            total_score += score
            total_correct += correct
            total_questions += total
            total_time += time

        avg_score = round(total_score / quiz_count, 1) if quiz_count > 0 else 0
        accuracy = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0

        user_stats.append({
            'username': username,
            'quiz_count': quiz_count,
            'average_score': avg_score,
            'total_correct': total_correct,
            'total_questions': total_questions,
            'accuracy': accuracy,
            'total_time': total_time
        })

    user_stats.sort(key=lambda x: x['average_score'], reverse=True)

    avg_all_users = 0
    if user_stats:
        avg_all_users = round(sum(u['average_score'] for u in user_stats) / len(user_stats), 1)

    return jsonify({
        'success': True,
        'data': {
            'users': user_stats,
            'total_users': len(user_stats),
            'average_score_all': avg_all_users
        }
    })
