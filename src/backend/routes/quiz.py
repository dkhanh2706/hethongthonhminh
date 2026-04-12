from flask import Blueprint, request, jsonify
from services.quiz_engine import (
    generate_quiz,
    check_answers,
    get_recommendation,
    get_next_quiz_mix,
    analyze_with_ml,
    analyze_with_fuzzy,
    compare_methods,
    save_quiz_session,
    get_quiz_history,
    get_all_quiz_history
)
from services.ml_model import get_predictor
from routes.questions import load_questions

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/quiz/start', methods=['POST'])
def start_quiz():
    data = request.json or {}
    mix = data.get("difficulty_mix", None)

    if mix:
        mix = {k: int(v) for k, v in mix.items()}

    questions = generate_quiz(mix)
    return jsonify({
        "success": True,
        "questions": questions,
        "total": len(questions)
    })


@quiz_bp.route('/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    username = data.get("username", "").strip()
    questions = data.get("questions", [])
    answers = data.get("answers", {})
    study_time = float(data.get("study_time", 30))

    if not questions:
        return jsonify({"success": False, "message": "Không có câu hỏi"}), 400

    result = check_answers(questions, answers)

    recommendation = get_recommendation(result["correct_count"], result["total"])

    next_mix = get_next_quiz_mix(recommendation["level"])

    mistakes = result["total"] - result["correct_count"]
    score = result["score"]

    ml_result = analyze_with_ml(score, study_time, mistakes)

    previous_score = 50.0
    if username:
        history = get_quiz_history(username)
        if history:
            previous_score = history[-1].get("score", 50.0)

    improvement = score - previous_score
    fuzzy_result = analyze_with_fuzzy(score, study_time, improvement)

    session_data = {
        "score": score,
        "correct_count": result["correct_count"],
        "total": result["total"],
        "study_time": study_time,
        "mistakes": mistakes,
        "questions": questions,
        "recommendation": recommendation,
        "ml_analysis": ml_result,
        "fuzzy_analysis": fuzzy_result,
        "next_mix": next_mix
    }

    if username:
        save_quiz_session(username, session_data)

    return jsonify({
        "success": True,
        "result": result,
        "recommendation": recommendation,
        "next_quiz_mix": next_mix,
        "ml_analysis": ml_result,
        "fuzzy_analysis": fuzzy_result
    })


@quiz_bp.route('/quiz/analyze', methods=['POST'])
def analyze_student():
    data = request.json
    score = float(data.get("score", 50))
    study_time = float(data.get("study_time", 30))
    mistakes = int(data.get("mistakes", 0))
    improvement = float(data.get("improvement", 0))

    ml_result = analyze_with_ml(score, study_time, mistakes)
    fuzzy_result = analyze_with_fuzzy(score, study_time, improvement)
    comparison = compare_methods(score, study_time, improvement)

    return jsonify({
        "success": True,
        "ml_analysis": ml_result,
        "fuzzy_analysis": fuzzy_result,
        "comparison": comparison
    })


@quiz_bp.route('/quiz/compare', methods=['POST'])
def compare():
    data = request.json
    score = float(data.get("score", 50))
    study_time = float(data.get("study_time", 30))
    improvement = float(data.get("improvement", 0))

    result = compare_methods(score, study_time, improvement)

    return jsonify({
        "success": True,
        "comparison": result
    })


@quiz_bp.route('/quiz/history', methods=['POST'])
def history():
    data = request.json
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "Thiếu tên người dùng"}), 400

    sessions = get_quiz_history(username)
    return jsonify({
        "success": True,
        "history": sessions
    })


@quiz_bp.route('/quiz/ml-metrics', methods=['GET'])
def ml_metrics():
    predictor = get_predictor()
    return jsonify({
        "success": True,
        "metrics": predictor.training_metrics
    })


@quiz_bp.route('/quiz/history/all', methods=['GET'])
def all_history():
    sessions = get_all_quiz_history()
    return jsonify({
        "success": True,
        "history": sessions
    })


@quiz_bp.route('/quiz/suggestions', methods=['POST'])
def get_suggestions():
    data = request.json
    username = data.get("username", "").strip()
    question_count = int(data.get("question_count", 10))
    
    if not username:
        return jsonify({"success": False, "message": "Thiếu tên người dùng"}), 400
    
    from services.adaptive_engine import recommend_questions
    suggestions = recommend_questions(username, count=5)
    
    return jsonify({
        "success": True,
        "suggestions": suggestions
    })


@quiz_bp.route('/quiz/lesson', methods=['POST'])
def get_lesson():
    data = request.json
    username = data.get("username", "").strip()
    
    if not username:
        return jsonify({"success": False, "message": "Thiếu tên người dùng"}), 400
    
    all_questions = load_questions()
    questions_list = all_questions.get("questions", [])
    
    if not questions_list or len(questions_list) == 0:
        return jsonify({
            "success": True,
            "lesson": [],
            "message": "Chưa có câu hỏi nào trong ngân hàng"
        })
    
    lesson_items = []
    for q in questions_list:
        lesson_items.append({
            "id": q.get("id", ""),
            "content": q.get("content", ""),
            "difficulty": q.get("difficulty", "normal"),
            "correct_answer": q.get("correct_answer", ""),
            "options": q.get("options", []),
            "topic": q.get("topic", "General")
        })
    
    return jsonify({
        "success": True,
        "lesson": lesson_items,
        "total": len(lesson_items)
    })
