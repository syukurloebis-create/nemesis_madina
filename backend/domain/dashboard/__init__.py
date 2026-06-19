class DashboardMetrics:

    @staticmethod
    def chain_integrity(
        events
    ):

        if events >= 5:
            return 100

        if events >= 2:
            return 85

        return 50