from typing import Literal, Dict, Any
from dataclasses import dataclass
import time


WS_EVENT = Literal[
    "SYSTEM",
    "CONNECT",
    "DISCONNECT",
    "MESSAGE",
    "ERROR"
]


@dataclass
class WSEvent:
    type: WS_EVENT
    client_id: str
    payload: Dict[str, Any] = None
    ts: float = time.time()

    def to_dict(self):
        return {
            "type": self.type,
            "client_id": self.client_id,
            "payload": self.payload,
            "ts": self.ts
        }