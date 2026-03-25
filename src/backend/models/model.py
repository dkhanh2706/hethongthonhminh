def recommend_question(score, time):
    if score < 5:
        level = "Dễ"
    elif score < 8:
        level = "Trung bình"
    else:
        level = "Khó"

    if time > 120:
        level += " (tăng độ khó)"

    return {
        "level": level
    }