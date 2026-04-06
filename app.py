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
# SUGGESTIONS (mix Đoàn + tâm lý)
# ======================
SUGGESTIONS = [
    "Điều kiện vào đoàn",
    "Hoạt động đoàn",
    "Tôi cảm thấy stress vì học tập",
    "Tôi bị mất động lực học",
    "Làm sao để tự tin hơn?"
]

# ======================
# SMART MATCH
# ======================
def find_best_answer(user_input):
    user_input = user_input.lower()

    best_match = None
    highest_ratio = 0

    for item in FAQ:
        question = item["question"].lower()
        ratio = difflib.SequenceMatcher(None, user_input, question).ratio()

        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = item

    if highest_ratio > 0.4:
        return best_match["answer"]

    # fallback tâm lý
    if any(word in user_input for word in ["stress", "áp lực", "mệt", "chán"]):
        return "Có vẻ bạn đang khá mệt 😔 Hãy nghỉ ngắn một chút, uống nước và đừng ép bản thân quá nhé."

    if any(word in user_input for word in ["lo", "sợ", "bất an"]):
        return "Lo lắng là điều bình thường. Bạn không cần giải quyết mọi thứ ngay lập tức, cứ từng bước thôi."

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

        if "history" not in session:
            session["history"] = []

        session["history"].append(user_message)

        answer = find_best_answer(user_message)

        if not answer:
            suggestions_text = "\n".join(f"- {q}" for q in SUGGESTIONS)
            answer = f"""Mình chưa hiểu rõ câu hỏi 🤔  
Bạn có thể thử hỏi:
{suggestions_text}
"""

        return jsonify({"reply": answer})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "⚠️ Server đang bận, thử lại sau nhé!"})


@app.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)