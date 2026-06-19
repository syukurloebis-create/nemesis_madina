class MockLLM:
    """Mock LLM untuk testing tanpa API call."""
    
    async def predict_risk(self, text: str) -> float:
        """Simulasi risk score dari LLM."""
        if "kesehatan" in text.lower():
            return 0.65
        elif "pendidikan" in text.lower():
            return 0.45
        else:
            return 0.55
    
    async def explain_anomaly(self, anomaly_data: dict) -> str:
        """Simulasi explanation dari anomaly."""
        return f"Mock explanation for anomaly: {anomaly_data.get('type', 'unknown')}"
