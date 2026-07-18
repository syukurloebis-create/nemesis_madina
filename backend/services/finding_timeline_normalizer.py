class FindingTimelineNormalizer:


    @staticmethod
    def normalize(row):

        event_type = row.get(
            "type"
        )


        source_map = {

            "EVENT":
                "finding_events",

            "ACTION":
                "finding_action_logs",

            "REVIEW_DECISION":
                "finding_review_decisions"

        }


        return {

            "type":
                event_type,


            "event":
                row.get(
                    "event"
                )
                or
                row.get(
                    "event_type"
                ),


            "actor":
                row.get(
                    "actor"
                ),


            "notes":
                row.get(
                    "notes"
                ),


            "metadata":
                row.get(
                    "metadata"
                )
                or
                {},


            "source":
                source_map.get(
                    event_type,
                    "unknown"
                ),


            "timestamp":
                row.get(
                    "timestamp"
                )
                or
                row.get(
                    "created_at"
                )

        }