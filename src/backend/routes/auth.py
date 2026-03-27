from flask import Blueprint, request, jsonify
from models.user import register_user, login_user, verify_token, reset_password, logout_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({"success": False, "message": "Vui lòng điền đầy đủ thông tin"}), 400

    if len(username) < 3:
        return jsonify({"success": False, "message": "Tên đăng nhập phải có ít nhất 3 ký tự"}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự"}), 400

    result = register_user(username, email, password)
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


@auth_bp.route('/logout', methods=['POST'])
def logout():
    data = request.json
    username = data.get('username', '').strip()

    if not username:
        return jsonify({"success": False, "message": "Không hợp lệ"}), 400

    result = logout_user(username)
    return jsonify(result), 200
