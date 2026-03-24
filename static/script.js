const input = document.getElementById("user-input");
const chat = document.getElementById("chat-box");
const status = document.getElementById("status");

// ================= LOAD CHAT =================
window.onload = () => {
    loadChat();
};

// ================= SEND =================
async function sendMessage(text = null) {
    const message = text || input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    showTyping();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ message })
        });

        const data = await res.json();

        removeTyping();

        setTimeout(() => {
            addMessage(data.reply, "bot");
        }, 500);

    } catch {
        removeTyping();
        addMessage("⚠️ Lỗi server!", "bot");
    }
}

function sendQuick(text) {
    sendMessage(text);
}

// ================= ADD MESSAGE (FIX AVATAR + SAVE) =================
function addMessage(text, sender) {
    const div = document.createElement("div");
    div.className = "message " + sender;

    const avatarUrl = sender === "user"
        ? "https://i.imgur.com/6VBx3io.png"
        : "https://i.imgur.com/7k12EPD.png";

    const avatar = document.createElement("img");
    avatar.src = avatarUrl;

    // fallback nếu ảnh lỗi
    avatar.onerror = function () {
        const fallback = document.createElement("div");
        fallback.className = "avatar-fallback";
        fallback.innerText = sender === "user" ? "👤" : "🤖";
        this.replaceWith(fallback);
    };

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = text.replace(/\n/g, "<br>");

    div.appendChild(avatar);
    div.appendChild(bubble);

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;

    saveChat(); // 👈 lưu lịch sử
}

// ================= TYPING =================
function showTyping() {
    status.innerText = "🟡 Đang trả lời...";

    const div = document.createElement("div");
    div.id = "typing";
    div.className = "message bot";

    div.innerHTML = `
        <img src="https://i.imgur.com/7k12EPD.png">
        <div class="bubble">⏳ Đang suy nghĩ...</div>
    `;

    chat.appendChild(div);
}

function removeTyping() {
    const t = document.getElementById("typing");
    if (t) t.remove();
    status.innerText = "🟢 Sẵn sàng";
}

// ================= RESET =================
function resetChat() {
    chat.innerHTML = "";
    localStorage.removeItem("chatHistory");

    addMessage("Xin chào 👋 Mình hỗ trợ về Đoàn!", "bot");
}

// ================= HELP =================
function showHelp() {
    addMessage("Bạn có thể hỏi:\n- Điều kiện\n- Hoạt động\n- Điểm rèn luyện", "bot");
}

// ================= SAVE CHAT =================
function saveChat() {
    localStorage.setItem("chatHistory", chat.innerHTML);
}

// ================= LOAD CHAT =================
function loadChat() {
    const saved = localStorage.getItem("chatHistory");

    if (saved) {
        chat.innerHTML = saved;
    } else {
        addMessage("Xin chào 👋 Mình hỗ trợ về Đoàn!", "bot");
    }
}

// ================= EVENTS =================
document.getElementById("send-btn").onclick = () => sendMessage();

input.addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
});

// ================= DARK MODE =================
function toggleTheme() {
    const body = document.body;
    const btn = document.getElementById("theme-btn");

    body.classList.toggle("dark");

    if (body.classList.contains("dark")) {
        btn.innerText = "☀️";
        localStorage.setItem("theme", "dark");
    } else {
        btn.innerText = "🌙";
        localStorage.setItem("theme", "light");
    }
}

window.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("theme");
    const btn = document.getElementById("theme-btn");

    if (saved === "dark") {
        document.body.classList.add("dark");
        btn.innerText = "☀️";
    }
});