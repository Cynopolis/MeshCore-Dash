// chatbox.js

// Send chat message
async function sendChatMessage() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if (!msg) return;

    const res = await fetch("/send_message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ msg })
    });

    const data = await res.json();
    if (!data.error) {
        addMessageToWindow(msg, "sent");
        input.value = "";
        adjustTextareaHeight();
    } else {
        console.error(data.error);
    }
}

// Add message to chat window
function addMessageToWindow(msg, type) {
    const chatWindow = document.getElementById("chatWindow");
    const div = document.createElement("div");
    div.className = `message ${type}`;
    div.textContent = msg;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Auto-grow textarea
const chatInput = document.getElementById("chatInput");
if (chatInput) {
    chatInput.addEventListener("input", adjustTextareaHeight);
}

function adjustTextareaHeight() {
    chatInput.style.height = "auto";
    chatInput.style.height = `${chatInput.scrollHeight}px`;
}

// Poll for new messages every 3 seconds
async function pollMessages() {
    try {
        const res = await fetch("/messages");
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => addMessageToWindow(msg, "received"));
        }
    } catch (e) {
        console.error("Error polling messages:", e);
    }
}

// Start polling if chat window exists
if (document.getElementById("chatWindow")) {
    setInterval(pollMessages, 3000);
}
