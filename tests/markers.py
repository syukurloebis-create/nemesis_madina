# tests/markers.py

import pytest

# Unit test markers
pytestmark_unit = pytest.mark.unit

# Integration test markers
pytestmark_integration = pytest.mark.integration

# Performance test markers
pytestmark_performance = pytest.mark.performance

# Domain specific markers
pytestmark_event_store = pytest.mark.event_store
pytestmark_projection = pytest.mark.projection
pytestmark_security = pytest.mark.security
pytestmark_telemetry = pytest.mark.telemetry
pytestmark_core = pytest.mark.core