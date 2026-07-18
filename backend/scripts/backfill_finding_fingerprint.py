import asyncio
import hashlib
import json

from sqlalchemy import text

from backend.database import AsyncSessionLocal



def fingerprint(row):

    payload = {
        "case_id": row.case_id,
        "finding_type": row.finding_type,
        "detection_method": row.detection_method,
        "details": row.anomaly_details
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        raw.encode()
    ).hexdigest()



async def main():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            text("""
                SELECT
                    id,
                    case_id,
                    finding_type,
                    detection_method,
                    anomaly_details
                FROM findings
                WHERE fingerprint IS NULL
            """)
        )

        rows = result.fetchall()


        for row in rows:

            fp = fingerprint(row)

            await db.execute(
                text("""
                    UPDATE findings
                    SET fingerprint=:fp
                    WHERE id=:id
                """),
                {
                    "fp":fp,
                    "id":row.id
                }
            )


        await db.commit()

        print(
            f"Updated {len(rows)} findings"
        )



if __name__=="__main__":
    asyncio.run(main())