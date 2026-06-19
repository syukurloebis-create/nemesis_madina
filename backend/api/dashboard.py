@router.get("/metrics")
async def metrics():

    entities = await repo.get_all_entities()

    results = []

    for entity in entities:

        events = await repo.get_events_by_aggregate(
            entity["aggregate_id"]
        )

        result = intelligence_engine.evaluate(
            entity["aggregate_id"],
            events
        )

        results.append(result)

    return DashboardMetrics.summarize(
        results
    )