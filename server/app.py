from flask import Flask, request, jsonify, send_from_directory
import serial.tools.list_ports
from mesh_communicator import MeshCommunicator
from mesh_database import MeshDatabase
from mesh_message_handler import MeshMessageHandler
import os

app = Flask(__name__)

# Single global communicator instance
mesh = MeshCommunicator()

# Database and message handler
db = MeshDatabase()
db.initializeDatabase()
message_handler = MeshMessageHandler(mesh, db)

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


@app.route("/chatbox.js")
def chatbox_js():
    """Serve JavaScript file"""
    return send_from_directory(FRONTEND_DIR, "chatbox.js")


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
    Send a message to the currently selected recipient via MeshMessageHandler.
    """
    data = request.json
    response = {"error": "Missing 'msg'"}
    response_code = 400

    if data is not None:
        msg = data.get("msg")
        if msg:
            response = message_handler.send_message(msg)

            response_code = 200
            if "error" in response:
                response_code = 400

    return jsonify(response), response_code


@app.route("/messages", methods=["GET"])
def get_messages():
    """
    Fetch the most recent messages from the database.
    """
    num_messages = request.args.get("num", default=50, type=int)
    messages = message_handler.get_last_messages(num_messages)
    # Convert MeshMessage objects to dicts for JSON serialization
    messages_data = [msg.__dict__ for msg in messages]
    return jsonify({"messages": messages_data}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
