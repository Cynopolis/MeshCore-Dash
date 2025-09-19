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

// Populate dropdown immediately on page load
window.addEventListener("DOMContentLoaded", refreshDevices);