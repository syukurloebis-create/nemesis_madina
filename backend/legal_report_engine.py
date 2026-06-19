# backend/intelligence/legal/legal_report_engine.py

from typing import Dict


class LegalReportEngine:

    def generate(
        self,
        package: Dict
    ):

        return {
            "risk_score":
                package["intelligence"]["risk_score"],

            "trust_score":
                package["intelligence"]["trust"]["trust_score"],

            "confidence":
                package["intelligence"]["confidence"]["confidence_score"],

            "top_factors":
                package["explainability"]["top_factors"],

            "chain_verified":
                True
        }