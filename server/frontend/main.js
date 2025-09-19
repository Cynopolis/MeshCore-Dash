// Populate the serial devices dropdown
async function refreshDevices() {
    const res = await fetch("/devices");
    const data = await res.json();
    const select = document.getElementById("serialDevice");
    select.innerHTML = ""; // clear existing options

    if (data.devices && data.devices.length > 0) {
        data.devices.forEach(dev => {
            const option = document.createElement("option");
            option.value = dev.device;
            option.textContent = `${dev.device} (${dev.description})`;
            select.appendChild(option);
        });
    } else {
        const option = document.createElement("option");
        option.textContent = "No devices found";
        option.value = "";
        select.appendChild(option);
    }
}

// Connect to selected device
async function connectDevice() {
    const select = document.getElementById("serialDevice");
    const port = select.value;

    const responseDiv = document.getElementById("connectResponse");
    if (!port) {
        responseDiv.textContent = "No device selected";
        return;
    }

    const res = await fetch("/connect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ port })
    });

    const data = await res.json();
    responseDiv.textContent = data.status || data.error;
}

async function sendAdvert() {
    const res = await fetch("/advert", { method: "POST" });
    const data = await res.json();
    document.getElementById("advertResponse").textContent = data.output || data.error;
}

async function sendFloodAdv() {
    const res = await fetch("/floodadv", { method: "POST" });
    const data = await res.json();
    document.getElementById("advertResponse").textContent = data.output || data.error;
}

async function listNodes() {
    const res = await fetch("/nodes");
    const data = await res.json();
    const nodeList = document.getElementById("nodeList");
    nodeList.innerHTML = "";
    if (data.output) {
        const nodes = data.output.split("\n");
        nodes.forEach(node => {
            const li = document.createElement("li");
            li.textContent = node;
            nodeList.appendChild(li);
        });
    } else if (data.error) {
        const li = document.createElement("li");
        li.textContent = data.error;
        li.className = "error";
        nodeList.appendChild(li);
    }
}

async function setRecipient() {
    const name = document.getElementById("recipient").value;
    const res = await fetch("/recipient", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });
    const data = await res.json();
    document.getElementById("recipientResponse").textContent = data.status || data.error;
}

async function sendMessage() {
    const msg = document.getElementById("messageText").value;
    const res = await fetch("/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ msg })
    });
    const data = await res.json();
    document.getElementById("messageResponse").textContent = data.output || data.error;
}
let lastMessageId = 0; // track last message id for polling

// Send chat message
async function sendChatMessage() {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if (!msg) return;

    const res = await fetch("/message", {
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
chatInput.addEventListener("input", adjustTextareaHeight);

function adjustTextareaHeight() {
    chatInput.style.height = "auto";
    chatInput.style.height = `${chatInput.scrollHeight}px`;
}

// Poll for new messages every second
async function pollMessages() {
    try {
        const res = await fetch("/messages"); // assumes backend returns { output: "msg1\nmsg2\n..." }
        const data = await res.json();
        if (data.output) {
            const messages = data.output.split("\n");
            messages.forEach(msg => addMessageToWindow(msg, "received"));
        }
    } catch (e) {
        console.error("Error polling messages:", e);
    }
}


// Start polling
setInterval(pollMessages, 3000);

// Populate dropdown immediately on page load
window.addEventListener("DOMContentLoaded", refreshDevices);