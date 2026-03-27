import json
import os
import time
import math
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
HISTORY_FILE = os.path.join(DATA_DIR, 'learning_history.json')
QUESTION_BANK_FILE = os.path.join(DATA_DIR, 'question_bank.json')

DIFFICULTY_LEVELS = {
    1: "Rất dễ",
    2: "Dễ",
    3: "Hơi dễ",
    4: "Trung bình",
    5: "Hơi khó",
    6: "Khó",
    7: "Khó",
    8: "Rất khó",
    9: "Thử thách",
    10: "Cực khó"
}

DIFFICULTY_NAMES = {
    "easy": "Dễ",
    "medium": "Trung bình",
    "hard": "Khó"
}


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


def _load_history():
    return _load_json(HISTORY_FILE, default={})


def _save_history(history):
    _save_json(HISTORY_FILE, history)


def _load_question_bank():
    return _load_json(QUESTION_BANK_FILE, default={"topics": {}})


def record_attempt(username, topic, subtopic, question_id, score, time_spent, is_correct):
    history = _load_history()

    if username not in history:
        history[username] = {
            "attempts": [],
            "topic_stats": {},
            "subtopic_stats": {},
            "level_profile": {},
            "created_at": datetime.now().isoformat()
        }

    user = history[username]

    attempt = {
        "topic": topic,
        "subtopic": subtopic,
        "question_id": question_id,
        "score": score,
        "time_spent": time_spent,
        "is_correct": is_correct,
        "timestamp": datetime.now().isoformat()
    }
    user["attempts"].append(attempt)

    if len(user["attempts"]) > 200:
        user["attempts"] = user["attempts"][-200:]

    _update_stats(user, topic, subtopic, score, time_spent, is_correct)
    _update_level_profile(user, topic, subtopic, score, time_spent)
    _save_history(history)

    return {"success": True, "message": "Đã ghi nhận kết quả"}


def _update_stats(user, topic, subtopic, score, time_spent, is_correct):
    key = f"{topic}.{subtopic}"
    stats = user["subtopic_stats"]

    if key not in stats:
        stats[key] = {
            "total_attempts": 0,
            "correct_count": 0,
            "total_score": 0,
            "total_time": 0,
            "scores": [],
            "times": [],
            "recent_scores": [],
            "recent_correct": []
        }

    s = stats[key]
    s["total_attempts"] += 1
    if is_correct:
        s["correct_count"] += 1
    s["total_score"] += score
    s["total_time"] += time_spent
    s["scores"].append(score)
    s["times"].append(time_spent)

    s["recent_scores"] = (s.get("recent_scores", []) + [score])[-10:]
    s["recent_correct"] = (s.get("recent_correct", []) + [1 if is_correct else 0])[-10:]

    topic_key = topic
    if topic_key not in user["topic_stats"]:
        user["topic_stats"][topic_key] = {
            "total_attempts": 0,
            "correct_count": 0,
            "total_score": 0,
            "subtopics_attempted": []
        }

    ts = user["topic_stats"][topic_key]
    ts["total_attempts"] += 1
    if is_correct:
        ts["correct_count"] += 1
    ts["total_score"] += score
    attempted = ts.get("subtopics_attempted", [])
    if isinstance(attempted, set):
        attempted = list(attempted)
    if subtopic not in attempted:
        attempted.append(subtopic)
    ts["subtopics_attempted"] = attempted


def _update_level_profile(user, topic, subtopic, score, time_spent):
    key = f"{topic}.{subtopic}"
    profile = user["level_profile"]

    if key not in profile:
        profile[key] = {
            "estimated_level": 5,
            "confidence": 0.1,
            "trend": "stable",
            "history_levels": []
        }

    p = profile[key]

    level_from_score = _score_to_level(score)
    alpha = min(0.5, 0.1 + p["confidence"] * 0.4)
    old_level = p["estimated_level"]
    p["estimated_level"] = old_level * (1 - alpha) + level_from_score * alpha
    p["estimated_level"] = max(1, min(10, p["estimated_level"]))

    p["confidence"] = min(1.0, p["confidence"] + 0.05)
    p["history_levels"].append(round(p["estimated_level"], 2))
    if len(p["history_levels"]) > 20:
        p["history_levels"] = p["history_levels"][-20:]

    if len(p["history_levels"]) >= 3:
        recent = p["history_levels"][-3:]
        if recent[-1] > recent[0] + 0.5:
            p["trend"] = "improving"
        elif recent[-1] < recent[0] - 0.5:
            p["trend"] = "declining"
        else:
            p["trend"] = "stable"


def _score_to_level(score):
    if score >= 95:
        return 9
    elif score >= 85:
        return 7
    elif score >= 75:
        return 6
    elif score >= 65:
        return 5
    elif score >= 50:
        return 4
    elif score >= 35:
        return 3
    elif score >= 20:
        return 2
    else:
        return 1


def analyze_student(username):
    history = _load_history()

    if username not in history:
        return {
            "status": "new_student",
            "message": "Chưa có dữ liệu học tập",
            "recommendations": _get_default_recommendations()
        }

    user = history[username]
    analysis = {
        "status": "active",
        "total_attempts": len(user["attempts"]),
        "weak_areas": _detect_weak_areas(user),
        "strong_areas": _detect_strong_areas(user),
        "learning_trends": _analyze_trends(user),
        "speed_accuracy_profile": _analyze_speed_accuracy(user),
        "topic_mastery": _calculate_topic_mastery(user),
        "optimal_difficulty": _predict_optimal_difficulty(user)
    }

    return analysis


def _detect_weak_areas(user):
    weak = []
    stats = user.get("subtopic_stats", {})

    for key, s in stats.items():
        if s["total_attempts"] < 2:
            continue

        accuracy = s["correct_count"] / s["total_attempts"]
        avg_score = s["total_score"] / s["total_attempts"]

        if accuracy < 0.5 or avg_score < 50:
            severity = "critical" if accuracy < 0.3 or avg_score < 30 else "warning"

            recent = s.get("recent_scores", [])
            if len(recent) >= 3:
                recent_avg = sum(recent[-3:]) / len(recent[-3:])
                overall_avg = avg_score
                if recent_avg < overall_avg - 10:
                    severity = "critical"

            weak.append({
                "subtopic": key,
                "accuracy": round(accuracy, 2),
                "avg_score": round(avg_score, 1),
                "severity": severity,
                "attempts": s["total_attempts"]
            })

    weak.sort(key=lambda x: (0 if x["severity"] == "critical" else 1, x["avg_score"]))
    return weak


def _detect_strong_areas(user):
    strong = []
    stats = user.get("subtopic_stats", {})

    for key, s in stats.items():
        if s["total_attempts"] < 2:
            continue

        accuracy = s["correct_count"] / s["total_attempts"]
        avg_score = s["total_score"] / s["total_attempts"]

        if accuracy >= 0.75 and avg_score >= 70:
            strong.append({
                "subtopic": key,
                "accuracy": round(accuracy, 2),
                "avg_score": round(avg_score, 1),
                "attempts": s["total_attempts"]
            })

    strong.sort(key=lambda x: -x["avg_score"])
    return strong


def _analyze_trends(user):
    attempts = user.get("attempts", [])
    if len(attempts) < 3:
        return {"overall": "insufficient_data"}

    recent = attempts[-10:]
    older = attempts[-20:-10] if len(attempts) >= 20 else attempts[:max(1, len(attempts) - 10)]

    recent_avg = sum(a["score"] for a in recent) / len(recent)
    older_avg = sum(a["score"] for a in older) / len(older) if older else recent_avg

    diff = recent_avg - older_avg
    if diff > 10:
        overall = "improving"
    elif diff < -10:
        overall = "declining"
    else:
        overall = "stable"

    time_recent = sum(a["time_spent"] for a in recent) / len(recent)
    time_older = sum(a["time_spent"] for a in older) / len(older) if older else time_recent

    speed_trend = "faster" if time_recent < time_older * 0.8 else ("slower" if time_recent > time_older * 1.2 else "consistent")

    return {
        "overall": overall,
        "score_change": round(diff, 1),
        "speed_trend": speed_trend,
        "recent_avg_score": round(recent_avg, 1),
        "older_avg_score": round(older_avg, 1)
    }


def _analyze_speed_accuracy(user):
    attempts = user.get("attempts", [])
    if not attempts:
        return {"profile": "unknown"}

    fast_correct = 0
    fast_total = 0
    slow_correct = 0
    slow_total = 0

    times = [a["time_spent"] for a in attempts]
    median_time = sorted(times)[len(times) // 2] if times else 10

    for a in attempts:
        if a["time_spent"] <= median_time:
            fast_total += 1
            if a["is_correct"]:
                fast_correct += 1
        else:
            slow_total += 1
            if a["is_correct"]:
                slow_correct += 1

    fast_acc = fast_correct / fast_total if fast_total > 0 else 0
    slow_acc = slow_correct / slow_total if slow_total > 0 else 0

    if fast_acc > 0.7 and slow_acc > 0.7:
        profile = "balanced"
    elif fast_acc > slow_acc + 0.1:
        profile = "speed_focused"
    elif slow_acc > fast_acc + 0.1:
        profile = "accuracy_focused"
    elif fast_acc < 0.4 and slow_acc < 0.4:
        profile = "needs_practice"
    else:
        profile = "developing"

    return {
        "profile": profile,
        "fast_accuracy": round(fast_acc, 2),
        "slow_accuracy": round(slow_acc, 2),
        "median_time": round(median_time, 1),
        "recommendation": _speed_accuracy_recommendation(profile, fast_acc, slow_acc)
    }


def _speed_accuracy_recommendation(profile, fast_acc, slow_acc):
    if profile == "speed_focused":
        return "Bạn làm nhanh nhưng cần chú ý độ chính xác. Hãy thử các câu khó hơn để rèn luyện kỹ năng."
    elif profile == "accuracy_focused":
        return "Bạn làm chính xác nhưng hơi chậm. Hãy luyện tập thêm để tăng tốc độ xử lý."
    elif profile == "needs_practice":
        return "Cần luyện tập thêm ở cả tốc độ và độ chính xác. Bắt đầu với câu dễ để xây dựng nền tảng."
    elif profile == "balanced":
        return "Tốc độ và độ chính xác khá cân bằng. Hãy thử thách bản thân với câu khó hơn."
    else:
        return "Tiếp tục luyện tập để cải thiện."


def _calculate_topic_mastery(user):
    mastery = {}
    stats = user.get("subtopic_stats", {})

    for key, s in stats.items():
        accuracy = s["correct_count"] / s["total_attempts"] if s["total_attempts"] > 0 else 0
        avg_score = s["total_score"] / s["total_attempts"] if s["total_attempts"] > 0 else 0

        recent = s.get("recent_correct", [])
        recent_acc = sum(recent) / len(recent) if recent else accuracy

        mastery_score = (accuracy * 0.3 + avg_score / 100 * 0.4 + recent_acc * 0.3) * 100

        if mastery_score >= 80:
            level = "Thành thạo"
        elif mastery_score >= 60:
            level = "Khá"
        elif mastery_score >= 40:
            level = "Trung bình"
        elif mastery_score >= 20:
            level = "Yếu"
        else:
            level = "Cần cải thiện"

        mastery[key] = {
            "score": round(mastery_score, 1),
            "level": level,
            "accuracy": round(accuracy, 2),
            "recent_accuracy": round(recent_acc, 2),
            "attempts": s["total_attempts"]
        }

    return mastery


def _predict_optimal_difficulty(user):
    profile = user.get("level_profile", {})
    if not profile:
        return {"level": 4, "label": "Trung bình", "confidence": 0.1}

    total_weight = 0
    weighted_level = 0

    for key, p in profile.items():
        weight = p["confidence"]
        level = p["estimated_level"]

        if p["trend"] == "improving":
            level += 0.5
        elif p["trend"] == "declining":
            level -= 0.5

        weighted_level += level * weight
        total_weight += weight

    if total_weight > 0:
        optimal = weighted_level / total_weight + 0.5
    else:
        optimal = 5

    optimal = max(1, min(9, optimal))

    level_label = DIFFICULTY_LEVELS.get(round(optimal), "Trung bình")

    avg_confidence = total_weight / len(profile) if profile else 0.1

    return {
        "level": round(optimal, 1),
        "label": level_label,
        "confidence": round(avg_confidence, 2)
    }


def recommend_questions(username, count=5):
    analysis = analyze_student(username)

    if analysis["status"] == "new_student":
        return _build_new_student_recommendations(count)

    weak_areas = analysis.get("weak_areas", [])
    optimal = analysis.get("optimal_difficulty", {})
    target_level = optimal.get("level", 5)

    bank = _load_question_bank()
    topics = bank.get("topics", {})

    recommendations = []
    used_ids = set()

    history = _load_history()
    user = history.get(username, {})
    for a in user.get("attempts", []):
        used_ids.add(a.get("question_id", ""))

    for weak in weak_areas[:3]:
        subtopic_key = weak["subtopic"]
        topic_name, subtopic_name = subtopic_key.split(".", 1) if "." in subtopic_key else (subtopic_key, "")

        if topic_name in topics and subtopic_name in topics[topic_name].get("subtopics", {}):
            subtopic_data = topics[topic_name]["subtopics"][subtopic_name]
            questions = _get_questions_at_level(subtopic_data, target_level - 1, used_ids)

            for q in questions[:2]:
                recommendations.append({
                    "question": q,
                    "topic": topics[topic_name]["name"],
                    "subtopic": subtopic_data["name"],
                    "reason": f"Kỹ năng yếu - cần cải thiện (độ chính xác: {weak['accuracy']*100:.0f}%)",
                    "priority": "high" if weak["severity"] == "critical" else "medium"
                })
                used_ids.add(q["id"])

    remaining = count - len(recommendations)
    if remaining > 0:
        strong_areas = analysis.get("strong_areas", [])
        for strong in strong_areas[:2]:
            subtopic_key = strong["subtopic"]
            topic_name, subtopic_name = subtopic_key.split(".", 1) if "." in subtopic_key else (subtopic_key, "")

            if topic_name in topics and subtopic_name in topics[topic_name].get("subtopics", {}):
                subtopic_data = topics[topic_name]["subtopics"][subtopic_name]
                questions = _get_questions_at_level(subtopic_data, target_level + 1, used_ids)

                for q in questions[:1]:
                    if remaining <= 0:
                        break
                    recommendations.append({
                        "question": q,
                        "topic": topics[topic_name]["name"],
                        "subtopic": subtopic_data["name"],
                        "reason": "Thử thách nâng cao - phát triển kỹ năng mạnh",
                        "priority": "low"
                    })
                    used_ids.add(q["id"])
                    remaining -= 1

    if remaining > 0:
        for topic_name, topic_data in topics.items():
            for subtopic_name, subtopic_data in topic_data.get("subtopics", {}).items():
                if remaining <= 0:
                    break
                questions = _get_questions_at_level(subtopic_data, target_level, used_ids)
                for q in questions[:1]:
                    if remaining <= 0:
                        break
                    recommendations.append({
                        "question": q,
                        "topic": topic_data["name"],
                        "subtopic": subtopic_data["name"],
                        "reason": "Luyện tập bổ sung",
                        "priority": "low"
                    })
                    used_ids.add(q["id"])
                    remaining -= 1

    return {
        "recommendations": recommendations[:count],
        "analysis_summary": {
            "optimal_difficulty": optimal,
            "weak_areas_count": len(weak_areas),
            "strong_areas_count": len(analysis.get("strong_areas", [])),
            "overall_trend": analysis.get("learning_trends", {}).get("overall", "unknown"),
            "speed_accuracy": analysis.get("speed_accuracy_profile", {}).get("profile", "unknown")
        },
        "learning_strategy": _generate_learning_strategy(analysis)
    }


def _get_questions_at_level(subtopic_data, target_level, used_ids):
    questions = []
    all_questions = []

    for diff_cat in ["easy", "medium", "hard"]:
        for q in subtopic_data.get("questions", {}).get(diff_cat, []):
            if q["id"] not in used_ids:
                all_questions.append(q)

    all_questions.sort(key=lambda q: abs(q["difficulty"] - target_level))
    return all_questions[:3]


def _build_new_student_recommendations(count):
    bank = _load_question_bank()
    topics = bank.get("topics", {})
    recommendations = []

    for topic_name, topic_data in list(topics.items())[:2]:
        for subtopic_name, subtopic_data in list(topic_data.get("subtopics", {}).items())[:1]:
            easy_qs = subtopic_data.get("questions", {}).get("easy", [])
            for q in easy_qs[:2]:
                recommendations.append({
                    "question": q,
                    "topic": topic_data["name"],
                    "subtopic": subtopic_data["name"],
                    "reason": "Câu hỏi khởi đầu - xác định trình độ",
                    "priority": "medium"
                })

    return {
        "recommendations": recommendations[:count],
        "analysis_summary": {
            "optimal_difficulty": {"level": 3, "label": "Dễ", "confidence": 0.0},
            "weak_areas_count": 0,
            "strong_areas_count": 0,
            "overall_trend": "new_student",
            "speed_accuracy": "unknown"
        },
        "learning_strategy": {
            "title": "Bắt đầu học",
            "description": "Bạn là học sinh mới. Hãy hoàn thành các câu hỏi khởi đầu để hệ thống xác định trình độ và đưa ra gợi ý phù hợp.",
            "tips": [
                "Làm các câu hỏi từ dễ đến khó",
                "Không cần vội vàng, hãy đọc kỹ đề bài",
                "Ghi chú lại những phần chưa hiểu"
            ]
        }
    }


def _generate_learning_strategy(analysis):
    weak_areas = analysis.get("weak_areas", [])
    trends = analysis.get("learning_trends", {})
    speed_acc = analysis.get("speed_accuracy_profile", {})
    optimal = analysis.get("optimal_difficulty", {})

    strategy = {
        "title": "",
        "description": "",
        "tips": []
    }

    if trends.get("overall") == "improving":
        strategy["title"] = "Tiến bộ tốt"
        strategy["description"] = f"Điểm số đã tăng {trends.get('score_change', 0):.0f} điểm gần đây. Tiếp tục duy trì!"
        strategy["tips"].append("Thử tăng độ khó để phát triển thêm")
    elif trends.get("overall") == "declining":
        strategy["title"] = "Cần củng cố"
        strategy["description"] = f"Điểm số giảm {abs(trends.get('score_change', 0)):.0f} điểm. Hãy quay lại các kiến thức nền tảng."
        strategy["tips"].append("Ôn lại lý thuyết cơ bản trước khi làm bài mới")
        strategy["tips"].append("Dành thêm thời gian cho các câu hỏi khó")
    else:
        strategy["title"] = "Duy trì ổn định"
        strategy["description"] = "Kết quả ổn định. Hãy thử thách bản thân với mức độ cao hơn."
        strategy["tips"].append("Tăng dần độ khó của câu hỏi")

    if weak_areas:
        weak_names = [w["subtopic"].split(".")[-1].replace("_", " ").title() for w in weak_areas[:2]]
        strategy["tips"].append(f"Ưu tiên cải thiện: {', '.join(weak_names)}")

    sa_profile = speed_acc.get("profile", "")
    if sa_profile == "speed_focused":
        strategy["tips"].append("Chậm lại một chút để tăng độ chính xác")
    elif sa_profile == "accuracy_focused":
        strategy["tips"].append("Luyện thêm để cải thiện tốc độ làm bài")

    strategy["tips"].append(f"Mức độ tối ưu hiện tại: {optimal.get('label', 'Trung bình')} (Level {optimal.get('level', 5)})")

    return strategy


def get_student_dashboard(username):
    analysis = analyze_student(username)
    recommendations = recommend_questions(username, count=5)

    history = _load_history()
    user = history.get(username, {})
    attempts = user.get("attempts", [])

    total_time = sum(a["time_spent"] for a in attempts)
    total_correct = sum(1 for a in attempts if a["is_correct"])

    dashboard = {
        "username": username,
        "stats": {
            "total_questions": len(attempts),
            "total_correct": total_correct,
            "accuracy": round(total_correct / len(attempts) * 100, 1) if attempts else 0,
            "total_time_minutes": round(total_time, 1),
            "avg_time_per_question": round(total_time / len(attempts), 1) if attempts else 0
        },
        "analysis": analysis,
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat()
    }

    return dashboard


def _get_default_recommendations():
    bank = _load_question_bank()
    topics = bank.get("topics", {})
    recs = []

    for topic_name, topic_data in list(topics.items())[:1]:
        for subtopic_name, subtopic_data in list(topic_data.get("subtopics", {}).items())[:1]:
            easy_qs = subtopic_data.get("questions", {}).get("easy", [])
            for q in easy_qs[:3]:
                recs.append({
                    "question": q,
                    "topic": topic_data["name"],
                    "subtopic": subtopic_data["name"],
                    "reason": "Câu hỏi mặc định cho người mới",
                    "priority": "medium"
                })

    return recs
