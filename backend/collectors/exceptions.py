"""
Collector Exceptions.
"""


class CollectorNotFoundError(Exception):
    """Exception ketika collector tidak ditemukan."""
    
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Collector not found: {name}")