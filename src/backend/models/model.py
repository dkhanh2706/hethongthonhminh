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


def get_weekly_statistics():
    import json
    import os
    from datetime import datetime, timedelta

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    history_file = os.path.join(data_dir, 'quiz_history.json')

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
    except:
        history_data = {}

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    
    daily_data = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        
        worker_count = 0
        task_count = 0
        work_rate = 0
        
        for username, sessions in history_data.items():
            for session in sessions:
                if 'created_at' in session and session['created_at'].startswith(day_str):
                    worker_count += 1
                    task_count += session.get('total', 0)
        
        if task_count > 0 and worker_count > 0:
            work_rate = min((task_count / worker_count) * 10, 100)
        elif worker_count > 0:
            work_rate = 5
        
        daily_data.append({
            'day': day.strftime('%a'),
            'date': day_str,
            'worker_count': worker_count,
            'task_count': task_count,
            'work_rate': round(work_rate, 1)
        })

    total_workers = sum(d['worker_count'] for d in daily_data)
    total_tasks = sum(d['task_count'] for d in daily_data)

    return {
        'success': True,
        'data': {
            'week_start': start_of_week.strftime('%Y-%m-%d'),
            'week_end': today.strftime('%Y-%m-%d'),
            'total_workers': total_workers,
            'total_tasks': total_tasks,
            'daily_data': daily_data
        }
    }
