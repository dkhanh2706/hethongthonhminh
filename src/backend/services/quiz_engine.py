import json
import os
import random
from services.ml_model import get_predictor
from services.fuzzy_controller import get_controller

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
QUIZ_FILE = os.path.join(DATA_DIR, 'quiz_questions.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'quiz_history.json')


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _load_json(filepath, default=None):
    _ensure_data_dir()
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}


def _save_json(filepath, data):
    _ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_quiz_questions():
    return _load_json(QUIZ_FILE, default={"questions": []})


def _load_history():
    return _load_json(HISTORY_FILE, default={})


def _save_history(history):
    _save_json(HISTORY_FILE, history)


def generate_quiz(difficulty_mix=None):
    bank = _load_quiz_questions()
    all_questions = bank.get("questions", [])

    easy = [q for q in all_questions if q["difficulty"] == "easy"]
    normal = [q for q in all_questions if q["difficulty"] == "normal"]
    hard = [q for q in all_questions if q["difficulty"] == "hard"]

    if difficulty_mix is None:
        difficulty_mix = {"easy": 3, "normal": 3, "hard": 4}

    selected = []

    n_easy = min(difficulty_mix.get("easy", 3), len(easy))
    selected.extend(random.sample(easy, n_easy))

    n_normal = min(difficulty_mix.get("normal", 3), len(normal))
    selected.extend(random.sample(normal, n_normal))

    n_hard = min(difficulty_mix.get("hard", 4), len(hard))
    selected.extend(random.sample(hard, n_hard))

    random.shuffle(selected)

    quiz_questions = []
    for q in selected:
        options = list(q["options"])
        random.shuffle(options)
        quiz_questions.append({
            "id": q["id"],
            "content": q["content"],
            "difficulty": q["difficulty"],
            "options": options,
            "topic": q["topic"],
            "expected_time": q["expected_time"]
        })

    return quiz_questions


def check_answers(quiz_questions, answers):
    bank = _load_quiz_questions()
    question_map = {q["id"]: q for q in bank.get("questions", [])}

    results = []
    correct_count = 0

    for i, q in enumerate(quiz_questions):
        qid = q["id"]
        user_answer = answers.get(qid, "")
        correct_answer = question_map.get(qid, {}).get("correct_answer", "")
        is_correct = user_answer == correct_answer

        if is_correct:
            correct_count += 1

        results.append({
            "question_id": qid,
            "content": q["content"],
            "difficulty": q["difficulty"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "topic": q["topic"]
        })

    total = len(quiz_questions)
    score = round(correct_count / total * 100, 1) if total > 0 else 0

    return {
        "results": results,
        "correct_count": correct_count,
        "total": total,
        "score": score
    }


def get_recommendation(correct_count, total=10):
    recommendation = get_recommendation_by_count(total)
    recommendation["correct_count"] = correct_count
    recommendation["total"] = total
    return recommendation


def get_recommendation_by_count(question_count):
    if question_count < 5:
        return {
            "level": "easy",
            "level_label": "Dễ",
            "message": f"Bạn hoàn thành {question_count} câu. Hệ thống sẽ gợi ý câu hỏi dễ để củng cố kiến thức.",
            "suggestion": "Tập trung vào các kiến thức cơ bản, đọc kỹ lý thuyết trước khi làm bài."
        }
    elif question_count <= 8:
        return {
            "level": "normal",
            "level_label": "Trung bình",
            "message": f"Bạn hoàn thành {question_count} câu. Hệ thống sẽ gợi ý câu hỏi trung bình để nâng cao.",
            "suggestion": "Tiếp tục luyện tập với mức độ trung bình, xen kẽ câu dễ và khó."
        }
    else:
        return {
            "level": "hard",
            "level_label": "Khó",
            "message": f"Bạn hoàn thành {question_count} câu. Xuất sắc! Hệ thống sẽ gợi ý câu hỏi khó.",
            "suggestion": "Thử thách bản thân với các câu hỏi nâng cao và tổng hợp."
        }


def get_next_quiz_mix(recommendation_level):
    if recommendation_level == "easy":
        return {"easy": 5, "normal": 3, "hard": 2}
    elif recommendation_level == "normal":
        return {"easy": 3, "normal": 4, "hard": 3}
    else:
        return {"easy": 2, "normal": 3, "hard": 5}


def analyze_with_ml(score, study_time, mistakes):
    predictor = get_predictor()
    return predictor.predict(score, study_time, mistakes)


def analyze_with_fuzzy(score, study_time, improvement):
    controller = get_controller()
    return controller.compute(score, study_time, improvement)


def compare_methods(score, study_time, improvement):
    controller = get_controller()
    return controller.compare(score, study_time, improvement)


def save_quiz_session(username, session_data):
    from datetime import datetime
    history = _load_history()
    if username not in history:
        history[username] = []
    
    session_data["created_at"] = datetime.now().isoformat()
    session_data["session_id"] = "session_" + str(len(history[username]) + 1) + "_" + str(int(datetime.now().timestamp()))
    
    history[username].append(session_data)
    _save_history(history)


def get_quiz_history(username):
    history = _load_history()
    return history.get(username, [])


def get_all_quiz_history():
    history = _load_history()
    all_sessions = []
    for username, sessions in history.items():
        for session in sessions:
            all_sessions.append({
                "username": username,
                "session_id": session.get("session_id", ""),
                "score": session.get("score", 0),
                "correct_count": session.get("correct_count", 0),
                "total": session.get("total", 0),
                "study_time": session.get("study_time", 0),
                "created_at": session.get("created_at", ""),
                "recommendation": session.get("recommendation", {})
            })
    all_sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return all_sessions
