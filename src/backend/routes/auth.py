from flask import Blueprint, request, jsonify
from models.user import register_user, login_user, admin_login_user, verify_token, reset_password, logout_user, list_users, delete_user, change_user_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    code = data.get('code', '').strip()

    if not username or not email or not password:
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

    if len(username) < 3:
        return jsonify({"success": False, "message": "Tên đăng nhập phải có ít nhất 3 ký tự"}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự"}), 400

    result = register_user(username, email, password, code)
    if not result["success"]:
        return jsonify(result), 409

    return jsonify(result), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

    result = login_user(username, password)
    if not result["success"]:
        return jsonify(result), 401

    return jsonify(result), 200


@auth_bp.route('/verify', methods=['POST'])
def verify():
    data = request.json
    username = data.get('username', '').strip()
    token = data.get('token', '')

    if not username or not token:
        return jsonify({"valid": False}), 400

    is_valid = verify_token(username, token)
    return jsonify({"valid": is_valid}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email', '').strip()
    new_password = data.get('new_password', '')

    if not email or not new_password:
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự"}), 400

    result = reset_password(email, new_password)
    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    code = data.get('code', '').strip()

    if not username or not password or not code:
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

    result = admin_login_user(username, password, code)
    if not result["success"]:
        return jsonify(result), 401

    return jsonify(result), 200


@auth_bp.route('/admin/users', methods=['GET'])
def get_users():
    result = list_users()
    return jsonify(result), 200


@auth_bp.route('/admin/users/delete', methods=['POST'])
def remove_user():
    data = request.json
    username = data.get('username', '').strip()

    if not username:
        return jsonify({"success": False, "message": "Vui lòng cung cấp tên người dùng"}), 400

    result = delete_user(username)
    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@auth_bp.route('/admin/users/change-password', methods=['POST'])
def change_password_admin():
    data = request.json
    username = data.get('username', '').strip()
    new_password = data.get('new_password', '')

    if not username or not new_password:
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự"}), 400

    result = change_user_password(username, new_password)
    if not result["success"]:
        return jsonify(result), 404

    return jsonify(result), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.json
    username = data.get('username', '').strip()

    if not username:
        return jsonify({"success": False, "message": "Không hợp lệ"}), 400

    result = logout_user(username)
    return jsonify(result), 200


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.json
    username = data.get('username', '').strip()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not username or not current_password or not new_password:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Mật khẩu mới phải có ít nhất 6 ký tự"}), 400

    import json
    import os
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent.parent
    users_file = base_dir / 'data' / 'users.json'

    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
    except:
        return jsonify({"success": False, "message": "Lỗi đọc dữ liệu"}), 500

    users = users_data.get('users', [])
    user_found = None
    user_index = None

    for i, u in enumerate(users):
        if u.get('username') == username:
            user_found = u
            user_index = i
            break

    if not user_found:
        return jsonify({"success": False, "message": "Không tìm thấy người dùng"}), 404

    import hashlib
    current_hash = hashlib.sha256(current_password.encode()).hexdigest()
    if user_found.get('password') != current_hash:
        return jsonify({"success": False, "message": "Mật khẩu hiện tại không đúng"}), 401

    new_hash = hashlib.sha256(new_password.encode()).hexdigest()
    users[user_index]['password'] = new_hash

    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        return jsonify({"success": True, "message": "Đổi mật khẩu thành công"})
    except:
        return jsonify({"success": False, "message": "Lỗi lưu dữ liệu"}), 500
