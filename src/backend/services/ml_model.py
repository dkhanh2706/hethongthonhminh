import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
SESSIONS_FILE = os.path.join(DATA_DIR, 'student_sessions.json')


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _load_sessions():
    _ensure_data_dir()
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_sessions(sessions):
    _ensure_data_dir()
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def generate_training_data(n_samples=500):
    np.random.seed(42)

    scores = np.random.uniform(0, 100, n_samples)
    study_times = np.random.uniform(5, 120, n_samples)
    mistakes = np.random.randint(0, 10, n_samples)

    X = np.column_stack([scores, study_times, mistakes])

    y_ability = np.zeros(n_samples)
    for i in range(n_samples):
        ability_score = (
            scores[i] * 0.5 +
            (1 - mistakes[i] / 10.0) * 30 +
            min(study_times[i] / 120.0, 1.0) * 20
        )
        if ability_score >= 70:
            y_ability[i] = 2
        elif ability_score >= 40:
            y_ability[i] = 1
        else:
            y_ability[i] = 0

    y_improvement = np.zeros(n_samples)
    for i in range(n_samples):
        base_improvement = scores[i] - 50 + np.random.normal(0, 10)
        if study_times[i] > 60:
            base_improvement += 10
        if mistakes[i] < 3:
            base_improvement += 5
        y_improvement[i] = np.clip(base_improvement, -30, 30)

    return X, y_ability, y_improvement


class StudentAbilityPredictor:
    def __init__(self):
        self.ability_classifier = RandomForestClassifier(
            n_estimators=100, max_depth=5, random_state=42
        )
        self.improvement_regressor = GradientBoostingRegressor(
            n_estimators=100, max_depth=3, random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_metrics = {}

    def train(self, X=None, y_ability=None, y_improvement=None):
        if X is None:
            X, y_ability, y_improvement = generate_training_data()

        X_scaled = self.scaler.fit_transform(X)

        self.ability_classifier.fit(X_scaled, y_ability)
        ability_scores = cross_val_score(
            self.ability_classifier, X_scaled, y_ability, cv=5
        )

        self.improvement_regressor.fit(X_scaled, y_improvement)
        improvement_scores = cross_val_score(
            self.improvement_regressor, X_scaled, y_improvement, cv=5
        )

        self.is_trained = True
        self.training_metrics = {
            "ability_cv_mean": round(ability_scores.mean(), 4),
            "ability_cv_std": round(ability_scores.std(), 4),
            "improvement_cv_mean": round(improvement_scores.mean(), 4),
            "improvement_cv_std": round(improvement_scores.std(), 4),
            "n_samples": len(X)
        }

        return self.training_metrics

    def predict(self, score, study_time, mistakes):
        if not self.is_trained:
            self.train()

        X = np.array([[score, study_time, mistakes]])
        X_scaled = self.scaler.transform(X)

        ability_pred = self.ability_classifier.predict(X_scaled)[0]
        ability_proba = self.ability_classifier.predict_proba(X_scaled)[0]

        improvement_pred = self.improvement_regressor.predict(X_scaled)[0]

        ability_labels = {0: "Yếu", 1: "Trung bình", 2: "Giỏi"}

        if improvement_pred > 5:
            trend = "increase"
        elif improvement_pred < -5:
            trend = "decrease"
        else:
            trend = "stable"

        return {
            "ability_level": int(ability_pred),
            "ability_label": ability_labels.get(int(ability_pred), "Không xác định"),
            "ability_probabilities": {
                "weak": round(float(ability_proba[0]), 3),
                "medium": round(float(ability_proba[1]), 3) if len(ability_proba) > 1 else 0,
                "strong": round(float(ability_proba[2]), 3) if len(ability_proba) > 2 else 0
            },
            "improvement_score": round(float(improvement_pred), 2),
            "improvement_trend": trend,
            "training_metrics": self.training_metrics
        }

    def save_session(self, username, session_data):
        sessions = _load_sessions()
        if username not in sessions:
            sessions[username] = []
        sessions[username].append(session_data)
        _save_sessions(sessions)

    def get_student_history(self, username):
        sessions = _load_sessions()
        return sessions.get(username, [])

    def calculate_improvement_from_history(self, username):
        history = self.get_student_history(username)
        if len(history) < 2:
            return 0.0
        recent = history[-1].get("score", 50)
        previous = history[-2].get("score", 50)
        return round(recent - previous, 2)


_predictor = None


def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = StudentAbilityPredictor()
        _predictor.train()
    return _predictor
