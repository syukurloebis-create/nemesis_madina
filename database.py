import sqlite3
import pandas as pd
from datetime import datetime
import hashlib

class DatabaseManager:
    def __init__(self, db_path='rup_database.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rup_paket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomor_id VARCHAR(50) UNIQUE NOT NULL,
                nama_paket TEXT NOT NULL,
                pagu DECIMAL(20,2),
                jenis VARCHAR(50),
                tahun INTEGER,
                kategori VARCHAR(100),
                metode VARCHAR(100),
                bulan VARCHAR(50),
                lokasi VARCHAR(100),
                instansi VARCHAR(200),
                hash_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upload_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255),
                file_size INTEGER,
                total_records INTEGER,
                new_records INTEGER,
                duplicate_records INTEGER,
                status VARCHAR(50),
                error_message TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nomor_id ON rup_paket(nomor_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tahun ON rup_paket(tahun)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_instansi ON rup_paket(instansi)")
        
        conn.commit()
        conn.close()
        print("✓ Database initialized successfully")
    
    def check_duplicate(self, nomor_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rup_paket WHERE nomor_id = ?", (str(nomor_id),))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def insert_paket(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hash_data = self._generate_hash(data)
            cursor.execute("SELECT id, hash_data FROM rup_paket WHERE nomor_id = ?", (str(data['nomor_id']),))
            existing = cursor.fetchone()
            
            if existing:
                existing_id, existing_hash = existing
                if existing_hash != hash_data:
                    cursor.execute("""
                        UPDATE rup_paket 
                        SET nama_paket = ?, pagu = ?, jenis = ?, tahun = ?, 
                            kategori = ?, metode = ?, bulan = ?, lokasi = ?, 
                            instansi = ?, hash_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (data['nama_paket'], data['pagu'], data['jenis'], data['tahun'],
                          data['kategori'], data['metode'], data['bulan'], data['lokasi'],
                          data['instansi'], hash_data, existing_id))
                    conn.commit()
                    conn.close()
                    return True, "Data updated successfully", False
                else:
                    conn.close()
                    return False, "Data already exists (no changes)", True
            else:
                cursor.execute("""
                    INSERT INTO rup_paket 
                    (nomor_id, nama_paket, pagu, jenis, tahun, kategori, metode, 
                     bulan, lokasi, instansi, hash_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(data['nomor_id']), data['nama_paket'], data['pagu'], 
                      data['jenis'], data['tahun'], data['kategori'], data['metode'],
                      data['bulan'], data['lokasi'], data['instansi'], hash_data))
                conn.commit()
                conn.close()
                return True, "Data inserted successfully", False
                
        except Exception as e:
            conn.close()
            return False, str(e), False
    
    def _generate_hash(self, data):
        hash_string = f"{data['nomor_id']}|{data['nama_paket']}|{data['pagu']}|{data['jenis']}|{data['tahun']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def log_upload(self, filename, file_size, total_records, new_records, duplicate_records, status, error_msg=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO upload_log 
            (filename, file_size, total_records, new_records, duplicate_records, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename, file_size, total_records, new_records, duplicate_records, status, error_msg))
        conn.commit()
        conn.close()
    
    def get_all_data(self, limit=100, offset=0, filters=None):
        conn = self.get_connection()
        query = "SELECT * FROM rup_paket WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('tahun'):
                query += " AND tahun = ?"
                params.append(filters['tahun'])
            if filters.get('jenis'):
                query += " AND jenis = ?"
                params.append(filters['jenis'])
            if filters.get('instansi'):
                query += " AND instansi LIKE ?"
                params.append(f"%{filters['instansi']}%")
            if filters.get('search'):
                query += " AND (nama_paket LIKE ? OR nomor_id LIKE ?)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])
        
        query += " ORDER BY tahun DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def get_total_count(self, filters=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM rup_paket WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('tahun'):
                query += " AND tahun = ?"
                params.append(filters['tahun'])
            if filters.get('jenis'):
                query += " AND jenis = ?"
                params.append(filters['jenis'])
            if filters.get('instansi'):
                query += " AND instansi LIKE ?"
                params.append(f"%{filters['instansi']}%")
            if filters.get('search'):
                query += " AND (nama_paket LIKE ? OR nomor_id LIKE ?)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_statistics(self):
        conn = self.get_connection()
        stats = {}
        stats['total_records'] = pd.read_sql_query("SELECT COUNT(*) as count FROM rup_paket", conn)['count'][0]
        stats['by_year'] = pd.read_sql_query("""
            SELECT tahun, COUNT(*) as count, SUM(pagu) as total_pagu 
            FROM rup_paket 
            GROUP BY tahun 
            ORDER BY tahun
        """, conn).to_dict('records')
        stats['by_type'] = pd.read_sql_query("""
            SELECT jenis, COUNT(*) as count 
            FROM rup_paket 
            GROUP BY jenis
        """, conn).to_dict('records')
        stats['total_pagu'] = pd.read_sql_query("SELECT SUM(pagu) as total FROM rup_paket", conn)['total'][0] or 0
        stats['recent_uploads'] = pd.read_sql_query("""
            SELECT * FROM upload_log 
            ORDER BY uploaded_at DESC 
            LIMIT 10
        """, conn).to_dict('records')
        conn.close()
        return stats
    
    def delete_data(self, nomor_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rup_paket WHERE nomor_id = ?", (str(nomor_id),))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
