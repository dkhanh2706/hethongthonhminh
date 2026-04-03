from flask import Flask, request, jsonify
from flask_cors import CORS
from models.model import recommend_question
from routes.auth import auth_bp
from routes.learning import learning_bp
from routes.quiz import quiz_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(learning_bp)
app.register_blueprint(quiz_bp)

@app.route("/", methods=["GET"])
def home():
    return {"message": "Server đang chạy 🚀"}

if __name__ == "__main__":
    app.run(debug=True)
