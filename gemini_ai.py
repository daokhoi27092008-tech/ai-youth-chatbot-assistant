try:
    import google.generativeai as genai
    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel("gemini-pro")
    USE_AI = True
except:
    USE_AI = False


def ask_gemini(message, history, intent):

    # ===== PROMPT THEO NGỮ CẢNH =====
    role_map = {
        "doan": "Bạn là cán bộ Đoàn, trả lời về công tác Đoàn.",
        "giaovien": "Bạn là giáo viên, gợi ý hoạt động giáo dục.",
        "hocsinh": "Bạn là trợ lý giải thích cho học sinh dễ hiểu.",
        "khac": "Bạn là trợ lý AI thân thiện."
    }

    context = "\n".join([f"{h['role']}: {h['content']}" for h in history])

    prompt = f"""
    {role_map[intent]}

    Lịch sử hội thoại:
    {context}

    Người dùng: {message}

    Trả lời ngắn gọn, rõ ràng.
    """

    if USE_AI:
        try:
            res = model.generate_content(prompt)
            return res.text
        except:
            return "⚠️ Lỗi AI, thử lại sau."

    # ===== MOCK (CHẠY ĐƯỢC 100%) =====
    return f"(Mock AI) Bạn hỏi: '{message}' | intent: {intent}"