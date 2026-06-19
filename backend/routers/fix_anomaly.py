@router.get("/anomaly/detection")
async def detect_anomalies(
    db: AsyncSession = Depends(get_db)
):
    """Detect anomalies in procurement patterns"""
    try:
        # Coba dengan kolom 'vendor' atau lihat struktur tabel
        result = await db.execute(
            text("""
                SELECT 
                    vendor as vendor_name,
                    COUNT(*) as package_count,
                    AVG(CAST(pagu AS DECIMAL)) as avg_value
                FROM rup_paket_detailed
                WHERE vendor IS NOT NULL AND pagu IS NOT NULL
                GROUP BY vendor
                HAVING COUNT(*) > 5
                ORDER BY avg_value DESC
                LIMIT 20
            """)
        )
        rows = result.fetchall()
        
        anomalies = []
        for row in rows:
            if row[2] and row[2] > 1000000000:
                anomalies.append({
                    "vendor": row[0],
                    "package_count": row[1],
                    "avg_value": float(row[2]),
                    "anomaly_score": min(100, (row[2] / 1000000000) * 50)
                })
        
        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "alert_level": "HIGH" if len(anomalies) > 5 else "MEDIUM" if len(anomalies) > 2 else "LOW"
        }
    except Exception as e:
        return {"error": str(e), "anomalies": []}
