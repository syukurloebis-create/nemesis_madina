def extract_from_case(case: Case):
    entities = []

    # =========================
    # FIX 1: FORCE READ METADATA
    # =========================
    metadata = case.case_metadata or {}

    companies = metadata.get("companies", [])
    suspects = metadata.get("suspects", [])
    transactions = metadata.get("transactions", [])

    # =========================
    # FIX 2: COMPANY NODES
    # =========================
    for c in companies:
        entities.append({
            "type": "company",
            "name": c,
            "confidence": 0.9,
            "source": "case_metadata"
        })

    # =========================
    # FIX 3: PERSON NODES
    # =========================
    for p in suspects:
        entities.append({
            "type": "person",
            "name": p,
            "confidence": 0.85,
            "source": "case_metadata"
        })

    # =========================
    # FIX 4: TRANSACTIONS → EDGES
    # =========================
    edges = []
    for t in transactions:
        edges.append({
            "source": t["from"],
            "target": t["to"],
            "type": "financial_transfer",
            "properties": {
                "amount": t.get("amount", 0)
            }
        })

    return entities, edges