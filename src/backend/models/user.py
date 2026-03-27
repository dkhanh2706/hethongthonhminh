import json
import os
import hashlib
import secrets

USERS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'users.json')


def _ensure_data_dir():
    data_dir = os.path.dirname(USERS_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def _load_users():
    _ensure_data_dir()
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_users(users):
    _ensure_data_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def register_user(username, email, password):
    users = _load_users()

    if username in users:
        return {"success": False, "message": "Tên đăng nhập đã tồn tại"}

    for user_data in users.values():
        if user_data.get("email") == email:
            return {"success": False, "message": "Email đã được sử dụng"}

    users[username] = {
        "email": email,
        "password": _hash_password(password),
        "token": None
    }
    _save_users(users)
    return {"success": True, "message": "Đăng ký thành công"}


def login_user(username, password):
    users = _load_users()

    if username not in users:
        return {"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng"}

    user = users[username]
    if user["password"] != _hash_password(password):
        return {"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng"}

    token = secrets.token_hex(32)
    users[username]["token"] = token
    _save_users(users)

    return {"success": True, "message": "Đăng nhập thành công", "token": token, "username": username}


def verify_token(username, token):
    users = _load_users()
    if username not in users:
        return False
    return users[username].get("token") == token


def reset_password(email, new_password):
    users = _load_users()

    found_username = None
    for username, user_data in users.items():
        if user_data.get("email") == email:
            found_username = username
            break

    if not found_username:
        return {"success": False, "message": "Không tìm thấy tài khoản với email này"}

    users[found_username]["password"] = _hash_password(new_password)
    users[found_username]["token"] = None
    _save_users(users)

    return {"success": True, "message": "Đặt lại mật khẩu thành công"}


def logout_user(username):
    users = _load_users()
    if username in users:
        users[username]["token"] = None
        _save_users(users)
    return {"success": True, "message": "Đã đăng xuất"}
