import threading
import time
from typing import List
from mesh_communicator import MeshCommunicator
from mesh_database import MeshDatabase, MeshMessage
from datetime import datetime


class MeshMessageHandler:
    def __init__(
        self,
        communicator: MeshCommunicator,
        database: MeshDatabase,
        poll_interval: float = 1.0
    ):
        """
        Initialize the handler.

        :param communicator: Instance of MeshCommunicator to fetch messages from
        :param database: Instance of MeshDatabase to store messages
        :param poll_interval: How often to poll the communicator (seconds)
        """
        self.communicator = communicator
        self.database = database
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._poll_thread = threading.Thread(
            target=self._poll_messages_loop, daemon=True
        )
        self._poll_thread.start()

    def _poll_messages_loop(self):
        """
        Background loop to continually fetch new messages from MeshCommunicator.
        """
        while not self._stop_event.is_set():
            try:
                result = self.communicator.get_messages()
                if "messages" in result:
                    for raw_msg in result["messages"]:
                        msg_obj = self._parse_raw_message(
                            raw_msg, sender="other")
                        self.database.store_message(msg_obj)
            except Exception as e:
                print(f"Error polling messages: {e}")
            time.sleep(self.poll_interval)

    def _parse_raw_message(self, raw_msg: str, sender: str = "unknown") -> MeshMessage:
        """
        Convert a raw meshcli message string into a MeshMessage object.
        """
        return MeshMessage(
            timestamp=datetime.utcnow().isoformat(),
            sender=sender,
            content=raw_msg,
            channel=None,
            is_dm=True
        )

    def send_message(self, msg_content: str) -> dict:
        """
        Create a MeshMessage, store it in the database, and send it via MeshCommunicator.
        """
        msg_obj = self._parse_raw_message(msg_content, sender="me")

        # Store in database first
        self.database.store_message(msg_obj)

        # Send via MeshCommunicator
        try:
            result = self.communicator.send_message(msg_content)
            if "error" in result:
                print(f"Error sending message: {result['error']}")
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_last_messages(self, num_messages: int) -> List[MeshMessage]:
        """
        Return the most recent `num_messages` stored in the database.
        """
        all_msgs = self.database.get_all_messages()
        return all_msgs[-num_messages:] if num_messages > 0 else all_msgs

    def stop(self):
        """
        Stop the polling loop.
        """
        self._stop_event.set()
        self._poll_thread.join()
