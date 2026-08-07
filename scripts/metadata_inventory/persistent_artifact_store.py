# persistent_artifact_store.py
import json
import sqlite3
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from immutable_dag import ArtifactEnvelope

class PersistentArtifactStore:
    """Persistent artifact store using SQLite."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY,
                name TEXT,
                version TEXT,
                schema_version TEXT,
                producer TEXT,
                timestamp TEXT,
                checksum TEXT,
                data_json TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_artifacts_name 
            ON artifacts(name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_artifacts_producer 
            ON artifacts(producer)
        """)
        
        conn.commit()
        conn.close()
    
    def put(self, envelope: ArtifactEnvelope) -> None:
        """Store an artifact envelope."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO artifacts 
            (artifact_id, name, version, schema_version, producer, timestamp, checksum, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            envelope.artifact_id,
            envelope.name,
            envelope.version,
            envelope.schema_version,
            envelope.producer,
            envelope.timestamp,
            envelope.checksum,
            json.dumps(envelope.data, default=str)
        ))
        
        conn.commit()
        conn.close()
    
    def get(self, artifact_id: str) -> Optional[ArtifactEnvelope]:
        """Retrieve an artifact by ID."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT artifact_id, name, version, schema_version, producer, timestamp, checksum, data_json "
            "FROM artifacts WHERE artifact_id = ?",
            (artifact_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ArtifactEnvelope(
                artifact_id=row[0],
                name=row[1],
                version=row[2],
                schema_version=row[3],
                producer=row[4],
                timestamp=row[5],
                checksum=row[6],
                data=json.loads(row[7])
            )
        return None
    
    def get_latest(self, name: str) -> Optional[ArtifactEnvelope]:
        """Get the latest version of an artifact."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT artifact_id, name, version, schema_version, producer, timestamp, checksum, data_json
            FROM artifacts 
            WHERE name = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ArtifactEnvelope(
                artifact_id=row[0],
                name=row[1],
                version=row[2],
                schema_version=row[3],
                producer=row[4],
                timestamp=row[5],
                checksum=row[6],
                data=json.loads(row[7])
            )
        return None
    
    def get_history(self, name: str) -> List[ArtifactEnvelope]:
        """Get all versions of an artifact."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT artifact_id, name, version, schema_version, producer, timestamp, checksum, data_json
            FROM artifacts 
            WHERE name = ? 
            ORDER BY timestamp DESC
        """, (name,))
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append(ArtifactEnvelope(
                artifact_id=row[0],
                name=row[1],
                version=row[2],
                schema_version=row[3],
                producer=row[4],
                timestamp=row[5],
                checksum=row[6],
                data=json.loads(row[7])
            ))
        return result
    
    def verify(self, artifact_id: str) -> bool:
        """Verify artifact checksum."""
        artifact = self.get(artifact_id)
        if not artifact:
            return False
        expected = hashlib.sha256(json.dumps(artifact.data, default=str, sort_keys=True).encode()).hexdigest()[:16]
        return artifact.checksum == expected