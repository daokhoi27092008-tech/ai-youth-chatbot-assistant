from flask import Flask, render_template, request, jsonify, session
import json
import difflib

app = Flask(__name__)
app.secret_key = "secret123"

# ======================
# LOAD DATA
# ======================
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

FAQ = data.get("faq", [])

# Danh sách câu hỏi gợi ý (lấy 5 câu đầu từ FAQ hoặc tự định nghĩa)
SUGGESTIONS = [
    "Điều kiện vào đoàn",
    "Số lượng đoàn viên",
    "Hoạt động đoàn",
    "Điểm rèn luyện là gì?",
    "Làm sao để tham gia hoạt động đoàn?"
]

# ======================
# SMART INTENT MATCH
# ======================
def find_best_answer(user_input):
    user_input = user_input.lower()

    # Lặp qua từng FAQ
    for item in FAQ:
        # Tạo danh sách câu có thể so khớp: question + aliases nếu có
        questions = [item["question"].lower()]
        if "aliases" in item:
            questions += [alias.lower() for alias in item["aliases"]]

        # So khớp gần đúng
        match = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.4)
        if match:
            return item["answer"]

    # keyword fallback
    if "bao nhiêu" in user_input or "số lượng" in user_input:
        return "Hiện tại đoàn trường có khoảng 500+ đoàn viên (cập nhật theo thực tế)."

    if "điều kiện" in user_input or "vào đoàn" in user_input:
        return "Bạn cần học sinh từ lớp 9 trở lên, có ý thức tốt và tham gia hoạt động."

    if "hoạt động" in user_input:
        return "Bao gồm văn nghệ, tình nguyện, thể thao, sinh hoạt định kỳ."

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

        # save history
        if "history" not in session:
            session["history"] = []

        session["history"].append(user_message)

        answer = find_best_answer(user_message)

        if not answer:
            suggestions_text = "\n".join(f"- {q}" for q in SUGGESTIONS)
            answer = f"""Mình chưa hiểu rõ câu hỏi 🤔  
Bạn có thể hỏi một trong các câu sau:
{suggestions_text}
"""

        return jsonify({"reply": answer})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "reply": "⚠️ Server đang bận, thử lại sau nhé!"
        })


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "ok"})


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)