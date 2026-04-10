from flask import Blueprint, request, jsonify
import json
import os

questions_bp = Blueprint('questions', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'quiz_questions.json')

def load_questions():
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"questions": []}

def save_questions(data):
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_id():
    data = load_questions()
    existing_ids = [q['id'] for q in data.get('questions', [])]
    for i in range(1, 1000):
        new_id = f"q{i:02d}"
        if new_id not in existing_ids:
            return new_id
    return f"q{len(existing_ids) + 1:02d}"


@questions_bp.route('/questions', methods=['GET'])
def list_questions():
    data = load_questions()
    return jsonify({
        "success": True,
        "questions": data.get('questions', [])
    })


@questions_bp.route('/questions/add', methods=['POST'])
def add_question():
    data = request.json
    
    content = data.get('content', '').strip()
    difficulty = data.get('difficulty', 'normal').strip().lower()
    correct_answer = data.get('correct_answer', '').strip()
    options = data.get('options', [])
    topic = data.get('topic', 'General').strip()
    expected_time = int(data.get('expected_time', 3))
    created_by = data.get('created_by', '').strip()
    
    if not content or not correct_answer or len(options) < 2:
        return jsonify({"success": False, "message": "Thiếu thông tin câu hỏi"}), 400
    
    if difficulty not in ['easy', 'normal', 'hard']:
        difficulty = 'normal'
    
    questions_data = load_questions()
    new_question = {
        "id": generate_id(),
        "content": content,
        "difficulty": difficulty,
        "correct_answer": correct_answer,
        "options": options[:4],
        "topic": topic,
        "expected_time": expected_time,
        "created_by": created_by
    }
    
    questions_data['questions'].append(new_question)
    save_questions(questions_data)
    
    return jsonify({
        "success": True,
        "message": "Thêm câu hỏi thành công",
        "question": new_question
    })


@questions_bp.route('/questions/update', methods=['POST'])
def update_question():
    data = request.json
    
    question_id = data.get('id', '').strip()
    content = data.get('content', '').strip()
    difficulty = data.get('difficulty', 'normal').strip().lower()
    correct_answer = data.get('correct_answer', '').strip()
    options = data.get('options', [])
    topic = data.get('topic', 'General').strip()
    expected_time = int(data.get('expected_time', 3))
    created_by = data.get('created_by', '').strip()
    
    if not question_id or not content or not correct_answer:
        return jsonify({"success": False, "message": "Thiếu thông tin câu hỏi"}), 400
    
    if difficulty not in ['easy', 'normal', 'hard']:
        difficulty = 'normal'
    
    questions_data = load_questions()
    questions = questions_data.get('questions', [])
    
    found = False
    for i, q in enumerate(questions):
        if q['id'] == question_id:
            questions[i] = {
                "id": question_id,
                "content": content,
                "difficulty": difficulty,
                "correct_answer": correct_answer,
                "options": options[:4] if options else q.get('options', []),
                "topic": topic,
                "expected_time": expected_time,
                "created_by": created_by or q.get('created_by', '')
            }
            found = True
            break
    
    if not found:
        return jsonify({"success": False, "message": "Không tìm thấy câu hỏi"}), 404
    
    save_questions(questions_data)
    
    return jsonify({
        "success": True,
        "message": "Cập nhật câu hỏi thành công"
    })


@questions_bp.route('/questions/delete', methods=['POST'])
def delete_question():
    data = request.json
    question_id = data.get('id', '').strip()
    
    if not question_id:
        return jsonify({"success": False, "message": "Thiếu ID câu hỏi"}), 400
    
    questions_data = load_questions()
    questions = questions_data.get('questions', [])
    
    new_questions = [q for q in questions if q['id'] != question_id]
    
    if len(new_questions) == len(questions):
        return jsonify({"success": False, "message": "Không tìm thấy câu hỏi"}), 404
    
    questions_data['questions'] = new_questions
    save_questions(questions_data)
    
    return jsonify({
        "success": True,
        "message": "Xóa câu hỏi thành công"
    })


@questions_bp.route('/questions/by-difficulty', methods=['POST'])
def questions_by_difficulty():
    data = request.json
    difficulty = data.get('difficulty', '').strip().lower()
    
    if difficulty not in ['easy', 'normal', 'hard']:
        return jsonify({"success": False, "message": "Sai mức độ khó"}), 400
    
    questions_data = load_questions()
    questions = [q for q in questions_data.get('questions', []) if q.get('difficulty') == difficulty]
    
    return jsonify({
        "success": True,
        "questions": questions,
        "count": len(questions)
    })