// main.js

// --- Serial Device Dropdown ---
async function refreshDevices() {
    const res = await fetch("/devices");
    const data = await res.json();
    const select = document.getElementById("serialDevice");
    if (!select) return;
    select.innerHTML = "";

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

async function connectDevice() {
    const select = document.getElementById("serialDevice");
    const port = select?.value;
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

// --- Advert / Flood ---
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

// --- Nodes ---
async function listNodes() {
    const res = await fetch("/nodes");
    const data = await res.json();
    const nodeList = document.getElementById("nodeList");
    nodeList.innerHTML = "";

    if (data.contacts) {
        data.contacts.forEach(node => {
            const li = document.createElement("li");
            li.textContent = node;
            nodeList.appendChild(li);
        });
    }
}

// --- Recipient ---
async function setRecipient() {
    const input = document.getElementById("recipient");
    const name = input.value.trim();
    const responseDiv = document.getElementById("recipientResponse");
    if (!name) {
        responseDiv.textContent = "Recipient name is empty";
        return;
    }

    const res = await fetch("/recipient", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });
    const data = await res.json();
    responseDiv.textContent = data.status || data.error;
}

// --- Initialize ---
window.addEventListener("DOMContentLoaded", refreshDevices);
