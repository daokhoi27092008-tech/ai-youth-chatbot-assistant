from flask import Flask, render_template, request, jsonify, session
import json
import difflib
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ======================
# LOAD DATA
# ======================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

FAQ = data.get("faq", [])

# ======================
# SUGGESTIONS
# ======================
SUGGESTIONS = [
    "Tiêu chuẩn vào đoàn là gì?",
    "Em bị bạn bắt nạt phải làm sao?",
    "Thi giáo dục STEM là gì?",
    "Hoạt động chào mừng 30/4 có gì?",
    "Em bị stress học tập"
]

# ======================
# NORMALIZE TEXT
# ======================
def normalize(text):
    return text.lower().strip()

# ======================
# FIND BEST MATCH
# ======================
def find_best_answer(user_input):
    user_input = normalize(user_input)

    best_match = None
    highest_score = 0

    for item in FAQ:
        question = normalize(item["question"])

        score = difflib.SequenceMatcher(None, user_input, question).ratio()

        # BONUS: keyword boost
        if any(word in user_input for word in question.split()):
            score += 0.1

        if score > highest_score:
            highest_score = score
            best_match = item

    if highest_score > 0.45:
        return best_match["answer"]

    return None

# ======================
# SMART FALLBACK
# ======================
def fallback_answer(user_input):
    user_input = normalize(user_input)

    if any(x in user_input for x in ["bắt nạt", "bạo lực"]):
        return "Bạn không nên im lặng. Hãy báo với thầy cô hoặc người lớn. Bạn xứng đáng được bảo vệ."

    if any(x in user_input for x in ["stress", "áp lực", "mệt"]):
        return "Bạn đang cố gắng rất nhiều rồi. Hãy nghỉ ngắn, uống nước và thư giãn nhé."

    if any(x in user_input for x in ["lo", "sợ"]):
        return "Lo lắng là bình thường. Bạn không cần giải quyết mọi thứ ngay lập tức."

    return None

# ======================
# ROUTES
# ======================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")

        if not user_message:
            return jsonify({"reply": "Bạn chưa nhập nội dung 🤔"})

        # lưu history
        session.setdefault("history", []).append(user_message)

        # tìm câu trả lời
        answer = find_best_answer(user_message)

        if not answer:
            answer = fallback_answer(user_message)

        if not answer:
            suggestions_text = "\n".join(f"- {q}" for q in SUGGESTIONS)
            answer = f"""Mình chưa hiểu rõ 🤔  
Bạn có thể hỏi:
{suggestions_text}
"""

        return jsonify({"reply": answer})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "⚠️ Server lỗi rồi 😢"})


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)