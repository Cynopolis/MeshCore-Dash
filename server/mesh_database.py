import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import os


@dataclass
class MeshMessage:
    timestamp: str
    sender: str
    content: str
    channel: Optional[str] = None
    is_dm: bool = True

    @staticmethod
    def from_json(packet: Dict[str, Any]) -> "MeshMessage":
        """
        Create a Message instance from a JSON packet.
        """
        return MeshMessage(
            timestamp=packet.get("timestamp", datetime.utcnow().isoformat()),
            sender=packet.get("sender", "unknown"),
            content=packet.get("content", ""),
            channel=packet.get("channel"),
            is_dm=packet.get("is_dm", True),
        )

    def to_db_tuple(self) -> tuple:
        """
        Generate a tuple suitable for inserting into the SQLite database.
        """
        return (self.timestamp, self.sender, self.content, self.channel, int(self.is_dm))

    @staticmethod
    def from_db_row(row: tuple) -> "MeshMessage":
        """
        Create a Message instance from a database row.
        """
        timestamp, sender, content, channel, is_dm = row
        return MeshMessage(
            timestamp=timestamp,
            sender=sender,
            content=content,
            channel=channel,
            is_dm=bool(is_dm)
        )


class MeshDatabase:
    def __init__(self, db_path: str = "database/meshdatabase.db") -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.initializeDatabase()

    def initializeDatabase(self) -> None:
        """
        Initialize the database, creating the messages table if it does not exist.
        """
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    channel TEXT,
                    is_dm INTEGER NOT NULL,
                    UNIQUE(timestamp, sender, content)
                )
                """
            )

    def store_message(self, message: MeshMessage) -> bool:
        """
        Store a message in the database if it isn't a duplicate.
        Returns True if stored, False if duplicate.
        """
        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT OR IGNORE INTO messages (timestamp, sender, content, channel, is_dm)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    message.to_db_tuple()
                )
            return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False

    def get_last_message(self) -> Optional[MeshMessage]:
        """
        Return the most recent message, or None if no messages exist.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT timestamp, sender, content, channel, is_dm FROM messages ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return MeshMessage.from_db_row(tuple(row))
        return None

    def get_all_messages(self) -> List[MeshMessage]:
        """
        Return all messages stored in the database.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT timestamp, sender, content, channel, is_dm FROM messages ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        return [MeshMessage.from_db_row(tuple(row)) for row in rows]

    def close(self):
        self.conn.close()
