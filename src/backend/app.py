from flask import Flask, request, jsonify
from flask_cors import CORS
from models.model import recommend_question

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return {"message": "Server đang chạy 🚀"}

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json

    score = float(data.get("score", 0))
    time = float(data.get("time", 0))

    result = recommend_question(score, time)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)