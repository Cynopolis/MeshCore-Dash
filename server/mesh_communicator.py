from __future__ import annotations
import subprocess
from typing import Optional, Dict, Any, Callable
from functools import wraps


def needsmeshdevice(func: Callable) -> Callable:
    """Decorator to ensure a serial device is selected before running a method."""
    @wraps(func)
    def wrapper(self: MeshCommunicator, *args, **kwargs) -> Dict[str, Any]:
        if not self.serial_device:
            return {"error": "No serial device selected"}
        return func(self, *args, **kwargs)
    return wrapper


def needsmeshrecipient(func: Callable) -> Callable:
    """Decorator to ensure both a serial device and recipient are selected."""
    @wraps(func)
    def wrapper(self: MeshCommunicator, *args, **kwargs) -> Dict[str, Any]:
        if not self.serial_device:
            return {"error": "No serial device selected"}
        if not self.target_recipient:
            return {"error": "No recipient selected"}
        return func(self, *args, **kwargs)
    return wrapper


class MeshCommunicator:
    def __init__(self) -> None:
        self.serial_device: Optional[str] = None
        self.target_recipient: Optional[str] = None

    def _run_meshcli(self, args: list[str]) -> Dict[str, Any]:
        """Run a meshcli command with the currently selected serial device."""
        cmd_args = ["meshcli"]
        if self.serial_device:
            cmd_args += ["-s", self.serial_device]
        cmd_args += args

        result = subprocess.run(cmd_args, capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr.strip() or "Unknown error"}
        return {"output": result.stdout.strip()}

    def set_serial_device(self, device: str) -> Dict[str, Any]:
        """Set the serial device path to use for meshcli commands."""
        self.serial_device = device
        return {"status": f"Serial device set to {device}"}

    def get_serial_device(self) -> Optional[str]:
        return self.serial_device

    def set_recipient(self, recipient: str) -> Dict[str, Any]:
        self.target_recipient = recipient
        return {"status": f"Recipient set to {recipient}"}

    def get_recipient(self) -> Optional[str]:
        return self.target_recipient

    @needsmeshdevice
    def send_advert(self) -> Dict[str, Any]:
        return self._run_meshcli(["advert"])

    @needsmeshdevice
    def send_floodadv(self) -> Dict[str, Any]:
        return self._run_meshcli(["floodadv"])

    @needsmeshdevice
    def list_nodes(self) -> Dict[str, Any]:
        return self._run_meshcli(["contacts"])

    @needsmeshrecipient
    def send_message(self, msg: str) -> Dict[str, Any]:
        assert self.target_recipient is not None
        return self._run_meshcli(["msg", self.target_recipient, msg])

    @needsmeshdevice
    def get_messages(self) -> Dict[str, Any]:
        """
        Fetch unread messages from the node.
        Returns a list of messages as JSON.
        """
        result = self._run_meshcli(["sync_msgs"])
        messages = []
        if "output" in result and result["output"]:
            messages = result["output"].splitlines()
        return {"messages": messages}
