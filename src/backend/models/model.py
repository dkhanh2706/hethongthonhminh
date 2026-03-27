from services.adaptive_engine import (
    recommend_questions,
    record_attempt,
    get_student_dashboard,
    analyze_student,
    _load_question_bank
)


def recommend_question(score, time):
    level_num = _score_to_legacy_level(score, time)

    levels = {1: "Dễ", 2: "Trung bình", 3: "Khó"}
    level = levels.get(level_num, "Trung bình")

    if time > 120:
        level += " (tăng độ khó)"

    return {
        "level": level,
        "level_num": level_num,
        "topic": "Tổng hợp",
        "difficulty": level_num,
        "reasoning": _get_legacy_reasoning(score, time),
        "strategy": _get_legacy_strategy(score, time)
    }


def _score_to_legacy_level(score, time):
    if score < 50:
        return 1
    elif score < 75:
        return 2
    else:
        return 3


def _get_legacy_reasoning(score, time):
    if score < 30:
        return "Điểm số rất thấp. Cần ôn lại kiến thức nền tảng trước."
    elif score < 50:
        return "Điểm số dưới trung bình. Nên luyện thêm các câu cơ bản."
    elif score < 75:
        return "Điểm số trung bình khá. Có thể thử câu hỏi mức trung bình."
    elif score < 90:
        return "Điểm số tốt. Hãy thử thách với câu hỏi khó hơn."
    else:
        return "Điểm số xuất sắc! Tiếp tục với các câu hỏi nâng cao."


def _get_legacy_strategy(score, time):
    if score < 50:
        return {
            "title": "Củng cố nền tảng",
            "description": "Tập trung vào lý thuyết cơ bản và các bài tập đơn giản.",
            "tips": [
                "Đọc kỹ lý thuyết trước khi làm bài",
                "Bắt đầu với các câu dễ để lấy lại tự tin",
                "Ghi chép lại công thức quan trọng"
            ]
        }
    elif score < 75:
        return {
            "title": "Phát triển đều",
            "description": "Cố gắng cân bằng giữa lý thuyết và bài tập.",
            "tips": [
                "Làm xen kẽ câu dễ và câu trung bình",
                "Ôn lại phần lý thuyết còn yếu",
                "Luyện thêm để tăng tốc độ làm bài"
            ]
        }
    else:
        return {
            "title": "Thử thách nâng cao",
            "description": "Bạn đã nắm vững cơ bản. Hãy thử sức với bài tập nâng cao.",
            "tips": [
                "Thử các câu hỏi khó để phát triển tư duy",
                "Kết hợp nhiều kiến thức trong một bài",
                "Luyện giải đề để kiểm tra toàn diện"
            ]
        }


def get_adaptive_recommendations(username, count=5):
    return recommend_questions(username, count)


def submit_answer(username, topic, subtopic, question_id, score, time_spent, is_correct):
    return record_attempt(username, topic, subtopic, question_id, score, time_spent, is_correct)


def get_dashboard(username):
    return get_student_dashboard(username)


def get_analysis(username):
    return analyze_student(username)


def get_question_bank():
    return _load_question_bank()
