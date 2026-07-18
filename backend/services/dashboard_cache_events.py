from backend.services.dashboard_cache_manager import (
    dashboard_cache_manager
)



def invalidate_finding_dashboard(
    finding_id: str
):

    dashboard_cache_manager.invalidate_finding(
        finding_id
    )


    dashboard_cache_manager.invalidate_kpi()