def build_transaction_edge(tx):
    return {
        "source": tx["from"],
        "target": tx["to"],
        "type": "financial_transfer",
        "properties": {
            "amount": tx.get("amount", 0),  # ✅ ONLY HERE
            "currency": "IDR",
            "timestamp": tx.get("timestamp")
        }
    }