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

    if (res.status === 200 && !data.error) {
        addMessageToWindow({
            sender: "me",
            content: msg
        });
    } else {
        // Display failed message with error from server
        const errorMsg = data.error || "Unknown error";
        addMessageToWindow({
            sender: "me",
            content: msg,
            failed: true,
            error: errorMsg
        });
        console.error(errorMsg);
    }

    input.value = "";
    adjustTextareaHeight();
}

// Add message to chat window
function addMessageToWindow(msgObj) {
    const chatWindow = document.getElementById("chatWindow");
    const div = document.createElement("div");

    // Determine message type for styling
    let type = "received";
    if (msgObj.sender === "me") type = "sent";
    if (msgObj.failed) type = "failed";

    div.className = `message ${type}`;
    div.textContent = msgObj.content;

    // Add a small submessage if failed
    if (msgObj.failed && msgObj.error) {
        const sub = document.createElement("div");
        sub.className = "failed-submessage";
        sub.textContent = `Failed to send: ${msgObj.error}`;
        div.appendChild(document.createElement("br"));
        div.appendChild(sub);
    }

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
