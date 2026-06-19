class MockAPIResponse:
    """Mock API response untuk testing endpoint."""
    
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self.data = data or {}
    
    def json(self):
        return self.data
    
    @property
    def ok(self):
        return 200 <= self.status_code < 300
