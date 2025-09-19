from flask import Flask, request, jsonify
import subprocess
import serial.tools.list_ports

app = Flask(__name__)

current_device = None
target_recipient = None


def run_meshcli(args):
    """Helper to run meshcli commands and capture output"""
    cmd = ["meshcli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return {"output": result.stdout.strip()}


@app.route("/devices", methods=["GET"])
def list_devices():
    """List connected serial devices"""
    ports = serial.tools.list_ports.comports()
    devices = [{"device": p.device, "description": p.description}
               for p in ports]
    return jsonify(devices)


@app.route("/connect", methods=["POST"])
def connect_device():
    """Connect to a serial device"""
    global current_device
    data = request.json
    port = data.get("port")
    if not port:
        return jsonify({"error": "Missing 'port'"}), 400
    current_device = port
    return jsonify({"status": f"Connected to {port}"})


@app.route("/advert", methods=["POST"])
def send_advert():
    """Send advert packet"""
    return jsonify(run_meshcli(["advert"]))


@app.route("/floodadv", methods=["POST"])
def send_floodadv():
    """Send flood advert packet"""
    return jsonify(run_meshcli(["floodadv"]))


@app.route("/nodes", methods=["GET"])
def list_nodes():
    """Get known nodes (contact list)"""
    return jsonify(run_meshcli(["contacts"]))


@app.route("/recipient", methods=["POST"])
def set_recipient():
    """Set the target recipient"""
    global target_recipient
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing 'name'"}), 400
    target_recipient = name
    return jsonify({"status": f"Recipient set to {name}"})


@app.route("/message", methods=["POST"])
def send_message():
    """Send a message to the target recipient"""
    if not target_recipient:
        return jsonify({"error": "Recipient not set"}), 400
    data = request.json
    msg = data.get("msg")
    if not msg:
        return jsonify({"error": "Missing 'msg'"}), 400
    return jsonify(run_meshcli(["msg", target_recipient, msg]))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
