from flask import Flask, request, jsonify, send_from_directory
import serial.tools.list_ports
from mesh_communicator import MeshCommunicator
import os

app = Flask(__name__)

# Single global communicator instance
mesh = MeshCommunicator()

# Path to the folder where index.html, main.js, and style.css are stored
FRONTEND_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "frontend")


@app.route("/")
def index():
    """Serve the main frontend page"""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/main.js")
def main_js():
    """Serve JavaScript file"""
    return send_from_directory(FRONTEND_DIR, "main.js")


@app.route("/style.css")
def style_css():
    """Serve CSS file"""
    return send_from_directory(FRONTEND_DIR, "style.css")


@app.route("/devices", methods=["GET"])
def list_devices():
    """List connected serial devices"""
    ports = serial.tools.list_ports.comports()
    devices = [{"device": p.device, "description": p.description}
               for p in ports]
    response = {"devices": devices}
    return jsonify(response), 200


@app.route("/messages", methods=["GET"])
def get_messages():
    """
    Fetch unread messages from the MeshCore node.
    """
    response = mesh.get_messages()
    return jsonify(response), 200


@app.route("/connect", methods=["POST"])
def connect_device():
    """Connect to a serial device"""
    data = request.json
    response = {"error": "Missing 'port'"}
    response_code: int = 400
    if data is not None:
        port = data.get("port")
        if port:
            response = mesh.set_serial_device(port)
            response_code = 200
    return jsonify(response), response_code


@app.route("/advert", methods=["POST"])
def send_advert():
    """Send advert packet"""
    response = mesh.send_advert()
    response_code = 200
    return jsonify(response), response_code


@app.route("/floodadv", methods=["POST"])
def send_floodadv():
    """Send flood advert packet"""
    response = mesh.send_floodadv()
    response_code = 200
    return jsonify(response), response_code


@app.route("/nodes", methods=["GET"])
def list_nodes():
    """Get known nodes (contact list)"""
    response = mesh.list_nodes()
    response_code = 200
    return jsonify(response), response_code


@app.route("/recipient", methods=["POST"])
def set_recipient():
    """Set the target recipient"""
    data = request.json
    response = {"error": "Missing 'name'"}
    response_code: int = 400
    if data is not None:
        name = data.get("name")
        if name:
            response = mesh.set_recipient(name)
            response_code = 200
    return jsonify(response), response_code


@app.route("/send_message", methods=["POST"])
def send_chat_message():
    """
    Send a message to the currently selected recipient via MeshCommunicator.
    """
    data = request.json
    response = {"error": "Missing 'msg'"}
    response_code = 400

    if data is not None:
        msg = data.get("msg")
        if msg:
            response = mesh.send_message(msg)
            response_code = 200

    return jsonify(response), response_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
