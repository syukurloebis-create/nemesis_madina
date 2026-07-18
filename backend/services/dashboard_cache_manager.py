import time


import time


class DashboardCacheManager:


    def __init__(self):

        self.cache = {}



    def get(
        self,
        namespace,
        key
    ):

        bucket = self.cache.get(
            namespace
        )


        if not bucket:
            return None


        item = bucket.get(
            key
        )


        if not item:
            return None


        return item["data"]



    def set(
        self,
        namespace,
        key,
        data
    ):

        if namespace not in self.cache:

            self.cache[namespace] = {}


        self.cache[namespace][key] = {

            "timestamp":
                time.time(),

            "data":
                data

        }



    def invalidate_namespace(
        self,
        namespace
    ):

        self.cache.pop(
            namespace,
            None
        )



    def invalidate_finding(
        self,
        finding_id
    ):

        self.invalidate(
            "finding_intelligence",
            finding_id
        )


        self.invalidate(
            "dashboard_intelligence_overview",
            "overview"
        )


        self.invalidate(
            "dashboard_kpi",
            "global"
        )

dashboard_cache_manager = DashboardCacheManager()