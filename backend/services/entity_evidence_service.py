from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class EntityEvidenceService:


    async def build_evidence(
        self,
        entity_id,
        entity_name,
        db: AsyncSession
    ):


        evidence = []


        #
        # Relationship evidence
        #

        result = await db.execute(
            text("""
            SELECT
                gr.relationship_type,
                gr.weight,
                s.name source,
                t.name target
            FROM graph_relationships gr

            JOIN graph_entities s
            ON s.id=gr.source_id

            JOIN graph_entities t
            ON t.id=gr.target_id

            WHERE
            (
                gr.source_id=:id
                OR
                gr.target_id=:id
            )

            ORDER BY gr.weight DESC
            LIMIT 50
            """),
            {
                "id":entity_id
            }
        )


        rows=result.mappings().all()



        identity=[]

        packages=[]

        methods=[]

        financial=[]



        for r in rows:


            if r["relationship_type"]=="same_entity_candidate":

                identity.append({

                    "vendor_a":r["source"],

                    "vendor_b":r["target"],

                    "similarity":
                    round(float(r["weight"]),2)

                })


            elif r["relationship_type"]=="shared_package":

                packages.append({

                    "vendor":
                    r["source"]
                    if r["target"]==entity_name
                    else r["target"],

                    "weight":
                    float(r["weight"])

                })


            elif r["relationship_type"]=="method_similarity":

                methods.append({

                    "vendor":
                    r["source"]
                    if r["target"]==entity_name
                    else r["target"],

                    "similarity":
                    float(r["weight"])

                })


            elif r["relationship_type"]=="financial_similarity":

                financial.append({

                    "vendor":
                    r["source"]
                    if r["target"]==entity_name
                    else r["target"],

                    "similarity":
                    float(r["weight"])

                })




        if identity:

            evidence.append({

                "type":
                "IDENTITY_MATCH",

                "severity":
                "HIGH",

                "count":
                len(identity),

                "details":
                identity

            })



        if packages:

            evidence.append({

                "type":
                "PACKAGE_COLLUSION_EVIDENCE",

                "severity":
                "HIGH",

                "count":
                len(packages),

                "details":
                packages

            })



        if methods:

            evidence.append({

                "type":
                "PROCUREMENT_BEHAVIOR",

                "severity":
                "MEDIUM",

                "count":
                len(methods),

                "details":
                methods

            })



        if financial:

            evidence.append({

                "type":
                "FINANCIAL_CLUSTER",

                "severity":
                "MEDIUM",

                "count":
                len(financial),

                "details":
                financial

            })



        return evidence




entity_evidence_service = EntityEvidenceService()