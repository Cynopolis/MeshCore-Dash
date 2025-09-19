// chatbox.js

// Keep track of messages already displayed
let displayedMessageIds = new Set();

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
        addMessageToWindow({
            sender: "me",
            content: msg
        });
        input.value = "";
        adjustTextareaHeight();
    } else {
        console.error(data.error);
    }
}

// Add message to chat window
function addMessageToWindow(msgObj) {
    const chatWindow = document.getElementById("chatWindow");
    const div = document.createElement("div");

    // Determine message type for styling
    const type = msgObj.sender === "me" ? "sent" : "received";
    div.className = `message ${type}`;
    div.textContent = msgObj.content;

    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Track that we've displayed this message
    if (msgObj.timestamp) {
        displayedMessageIds.add(msgObj.timestamp);
    }
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
        const res = await fetch("/messages?num=50");
        const data = await res.json();

        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                if (!displayedMessageIds.has(msg.timestamp)) {
                    addMessageToWindow(msg);
                }
            });
        }
    } catch (e) {
        console.error("Error polling messages:", e);
    }
}

// Load initial messages on page load
window.addEventListener("load", async () => {
    await pollMessages();
    // Start polling every 3 seconds
    setInterval(pollMessages, 3000);
});
