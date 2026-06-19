@router.post("/cases/{case_id}/extract-entities")
def extract_entities(case_id: str):
    
    case = case_service.get(case_id)

    # =========================
    # FIX: FORCE PIPELINE EXECUTION
    # =========================
    entities, edges = entity_extractor.extract_from_case(case)

    graph_store.save_entities(case_id, entities)
    graph_store.save_edges(case_id, edges)

    graph_summary = graph_store.get_summary(case_id)

    return {
        "case_id": case_id,
        "entities_extracted": len(entities),
        "entities_stored": len(entities),
        "transactions_stored": len(edges),
        "graph_summary": graph_summary
    }