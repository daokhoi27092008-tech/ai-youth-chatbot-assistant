from flask import Flask, render_template, request, jsonify, session
import json
import os

app = Flask(__name__)
app.secret_key = "secret123"

# LOAD DATA
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

FAQ = data.get("faq", [])

# GỢI Ý
SUGGESTIONS = [
    "Điều kiện vào đoàn",
    "Hoạt động đoàn",
    "Trường THPT Việt Lâm có hoạt động gì",
    "Tôi bị mất động lực học",
    "Tôi bị bạn bắt nạt phải làm sao?"
]

# CHUẨN HÓA TEXT
def normalize(text):
    return text.lower().strip()

# MATCH CHÍNH XÁC
def find_best_answer(user_input):
    user_input = normalize(user_input)

    # ƯU TIÊN MATCH 100%
    for item in FAQ:
        if normalize(item["question"]) == user_input:
            return item["answer"]

    # MATCH GẦN (contains)
    for item in FAQ:
        if normalize(item["question"]) in user_input:
            return item["answer"]

    return None

# FALLBACK THÔNG MINH
def fallback_answer(user_input):
    user_input = normalize(user_input)

    if user_input in ["xin chào", "hello", "hi"]:
        return "Xin chào 👋 Mình có thể hỗ trợ bạn về Đoàn hoặc tâm lý học đường."

    if any(x in user_input for x in ["bắt nạt", "bạo lực"]):
        return "Bạn không nên im lặng. Hãy báo với thầy cô hoặc người lớn. Bạn xứng đáng được bảo vệ."

    if any(x in user_input for x in ["stress", "áp lực", "mệt"]):
        return "Bạn đang cố gắng rất nhiều rồi. Hãy nghỉ ngắn và thư giãn nhé."

    if any(x in user_input for x in ["lo", "sợ"]):
        return "Lo lắng là bình thường. Hãy giải quyết từng bước nhỏ nhé."

    return None

# ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Bạn chưa nhập nội dung 🤔"})

        session.setdefault("history", []).append(user_message)

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