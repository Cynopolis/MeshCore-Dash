from flask import Flask, request, jsonify
import serial.tools.list_ports
from mesh_communicator import MeshCommunicator

app = Flask(__name__)

# Single global communicator instance
mesh = MeshCommunicator()


@app.route("/devices", methods=["GET"])
def list_devices():
    """List connected serial devices"""
    ports = serial.tools.list_ports.comports()
    devices = [{"device": p.device, "description": p.description}
               for p in ports]
    response = {"devices": devices}
    response_code = 200
    return jsonify(response), response_code


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


@app.route("/message", methods=["POST"])
def send_message():
    """Send a message to the target recipient"""
    data = request.json
    response = {"error": "Missing 'msg'"}
    response_code: int = 400
    if data is not None:
        msg = data.get("msg")
        if msg:
            response = mesh.send_message(msg)
            response_code = 200
    return jsonify(response), response_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
