from collections import deque
import time


class WSObservability:
    def __init__(self, maxlen=500):
        self.events = deque(maxlen=maxlen)

    def log(self, event: dict):
        event["server_ts"] = time.time()
        self.events.append(event)

    def snapshot(self):
        return list(self.events)