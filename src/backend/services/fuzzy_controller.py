import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class AdaptiveFuzzyController:
    def __init__(self):
        self.system = None
        self.simulation = None
        self._build_system()

    def _build_system(self):
        score = ctrl.Antecedent(np.arange(0, 101, 1), 'score')
        study_time = ctrl.Antecedent(np.arange(0, 121, 1), 'study_time')
        improvement = ctrl.Antecedent(np.arange(-30, 31, 1), 'improvement')

        difficulty = ctrl.Consequent(np.arange(0, 101, 1), 'difficulty')
        question_load = ctrl.Consequent(np.arange(0, 101, 1), 'question_load')

        score['low'] = fuzz.trimf(score.universe, [0, 0, 50])
        score['medium'] = fuzz.trimf(score.universe, [30, 55, 80])
        score['high'] = fuzz.trimf(score.universe, [60, 100, 100])

        study_time['short'] = fuzz.trimf(study_time.universe, [0, 0, 40])
        study_time['medium'] = fuzz.trimf(study_time.universe, [20, 55, 90])
        study_time['long'] = fuzz.trimf(study_time.universe, [60, 120, 120])

        improvement['decrease'] = fuzz.trimf(improvement.universe, [-30, -30, 0])
        improvement['stable'] = fuzz.trimf(improvement.universe, [-10, 0, 10])
        improvement['increase'] = fuzz.trimf(improvement.universe, [0, 30, 30])

        difficulty['easy'] = fuzz.trimf(difficulty.universe, [0, 0, 45])
        difficulty['medium'] = fuzz.trimf(difficulty.universe, [25, 50, 75])
        difficulty['hard'] = fuzz.trimf(difficulty.universe, [55, 100, 100])

        question_load['few'] = fuzz.trimf(question_load.universe, [0, 0, 40])
        question_load['normal'] = fuzz.trimf(question_load.universe, [25, 50, 75])
        question_load['many'] = fuzz.trimf(question_load.universe, [60, 100, 100])

        rules = [
            ctrl.Rule(score['low'] & study_time['short'] & improvement['decrease'],
                      (difficulty['easy'], question_load['few'])),

            ctrl.Rule(score['low'] & study_time['short'] & improvement['stable'],
                      (difficulty['easy'], question_load['few'])),

            ctrl.Rule(score['low'] & study_time['short'] & improvement['increase'],
                      (difficulty['easy'], question_load['normal'])),

            ctrl.Rule(score['low'] & study_time['medium'] & improvement['decrease'],
                      (difficulty['easy'], question_load['few'])),

            ctrl.Rule(score['low'] & study_time['medium'] & improvement['stable'],
                      (difficulty['easy'], question_load['normal'])),

            ctrl.Rule(score['low'] & study_time['medium'] & improvement['increase'],
                      (difficulty['medium'], question_load['normal'])),

            ctrl.Rule(score['low'] & study_time['long'] & improvement['decrease'],
                      (difficulty['easy'], question_load['normal'])),

            ctrl.Rule(score['low'] & study_time['long'] & improvement['stable'],
                      (difficulty['medium'], question_load['normal'])),

            ctrl.Rule(score['low'] & study_time['long'] & improvement['increase'],
                      (difficulty['medium'], question_load['many'])),

            ctrl.Rule(score['medium'] & study_time['short'] & improvement['decrease'],
                      (difficulty['easy'], question_load['normal'])),

            ctrl.Rule(score['medium'] & study_time['short'] & improvement['stable'],
                      (difficulty['medium'], question_load['normal'])),

            ctrl.Rule(score['medium'] & study_time['short'] & improvement['increase'],
                      (difficulty['medium'], question_load['many'])),

            ctrl.Rule(score['medium'] & study_time['medium'] & improvement['stable'],
                      (difficulty['medium'], question_load['normal'])),

            ctrl.Rule(score['medium'] & study_time['medium'] & improvement['increase'],
                      (difficulty['medium'], question_load['many'])),

            ctrl.Rule(score['medium'] & study_time['long'] & improvement['stable'],
                      (difficulty['medium'], question_load['many'])),

            ctrl.Rule(score['medium'] & study_time['long'] & improvement['increase'],
                      (difficulty['hard'], question_load['many'])),

            ctrl.Rule(score['high'] & study_time['short'] & improvement['stable'],
                      (difficulty['medium'], question_load['normal'])),

            ctrl.Rule(score['high'] & study_time['short'] & improvement['increase'],
                      (difficulty['hard'], question_load['normal'])),

            ctrl.Rule(score['high'] & study_time['medium'] & improvement['increase'],
                      (difficulty['hard'], question_load['many'])),

            ctrl.Rule(score['high'] & study_time['long'] & improvement['increase'],
                      (difficulty['hard'], question_load['many'])),

            ctrl.Rule(score['high'] & study_time['long'] & improvement['stable'],
                      (difficulty['hard'], question_load['normal'])),

            ctrl.Rule(score['high'] & study_time['medium'] & improvement['decrease'],
                      (difficulty['medium'], question_load['normal'])),

            ctrl.Rule(score['high'] & study_time['short'] & improvement['decrease'],
                      (difficulty['medium'], question_load['few'])),

            ctrl.Rule(score['medium'] & study_time['medium'] & improvement['decrease'],
                      (difficulty['easy'], question_load['normal'])),

            ctrl.Rule(score['medium'] & study_time['long'] & improvement['decrease'],
                      (difficulty['easy'], question_load['normal'])),
        ]

        self.system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(self.system)

    def compute(self, score_val, time_val, improvement_val):
        self.simulation.input['score'] = np.clip(score_val, 0, 100)
        self.simulation.input['study_time'] = np.clip(time_val, 0, 120)
        self.simulation.input['improvement'] = np.clip(improvement_val, -30, 30)

        try:
            self.simulation.compute()
            diff_raw = self.simulation.output['difficulty']
            load_raw = self.simulation.output['question_load']

            if diff_raw < 35:
                diff_label = "Dễ"
            elif diff_raw < 65:
                diff_label = "Trung bình"
            else:
                diff_label = "Khó"

            if load_raw < 35:
                load_label = "Ít"
            elif load_raw < 65:
                load_label = "Bình thường"
            else:
                load_label = "Nhiều"

            return {
                "difficulty_raw": round(float(diff_raw), 2),
                "difficulty_label": diff_label,
                "question_load_raw": round(float(load_raw), 2),
                "question_load_label": load_label
            }
        except Exception as e:
            return {
                "difficulty_raw": 50.0,
                "difficulty_label": "Trung bình",
                "question_load_raw": 50.0,
                "question_load_label": "Bình thường",
                "error": str(e)
            }

    def traditional_if_else(self, score_val, time_val, improvement_val):
        if score_val < 40:
            diff_label = "Dễ"
            diff_raw = 20.0
        elif score_val < 70:
            diff_label = "Trung bình"
            diff_raw = 50.0
        else:
            diff_label = "Khó"
            diff_raw = 80.0

        if improvement_val < -5:
            load_label = "Ít"
            load_raw = 25.0
        elif improvement_val > 5:
            load_label = "Nhiều"
            load_raw = 75.0
        else:
            load_label = "Bình thường"
            load_raw = 50.0

        if time_val < 30:
            load_raw = max(load_raw - 15, 10)
        elif time_val > 90:
            load_raw = min(load_raw + 10, 90)

        if load_raw < 35:
            load_label = "Ít"
        elif load_raw < 65:
            load_label = "Bình thường"
        else:
            load_label = "Nhiều"

        return {
            "difficulty_raw": round(diff_raw, 2),
            "difficulty_label": diff_label,
            "question_load_raw": round(load_raw, 2),
            "question_load_label": load_label
        }

    def compare(self, score_val, time_val, improvement_val):
        fuzzy_result = self.compute(score_val, time_val, improvement_val)
        if_else_result = self.traditional_if_else(score_val, time_val, improvement_val)

        return {
            "inputs": {
                "score": score_val,
                "study_time": time_val,
                "improvement": improvement_val
            },
            "fuzzy_logic": fuzzy_result,
            "traditional_if_else": if_else_result,
            "differences": {
                "difficulty_diff": round(
                    fuzzy_result["difficulty_raw"] - if_else_result["difficulty_raw"], 2
                ),
                "load_diff": round(
                    fuzzy_result["question_load_raw"] - if_else_result["question_load_raw"], 2
                ),
                "difficulty_match": fuzzy_result["difficulty_label"] == if_else_result["difficulty_label"],
                "load_match": fuzzy_result["question_load_label"] == if_else_result["question_load_label"]
            }
        }


_controller = None


def get_controller():
    global _controller
    if _controller is None:
        _controller = AdaptiveFuzzyController()
    return _controller
