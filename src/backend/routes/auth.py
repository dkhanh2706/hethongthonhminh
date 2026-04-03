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
