import pandas as pd
import os
from datetime import datetime

class FileProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.expected_columns = ['nama_paket', 'pagu', 'jenis', 'tahun', 'kategori', 
                                  'metode', 'bulan', 'lokasi', 'instansi', 'nomor_id']
    
    def process_file(self, file_path, filename):
        file_size = os.path.getsize(file_path)
        errors = []
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8', sep=None, engine='python')
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                return 0, 0, 0, ["Unsupported file format. Please upload CSV or Excel file."]
            
            missing_columns = [col for col in self.expected_columns if col not in df.columns]
            if missing_columns:
                return 0, 0, 0, [f"Missing required columns: {', '.join(missing_columns)}"]
            
            df = self._clean_data(df)
            
            new_records = 0
            duplicate_records = 0
            total_records = len(df)
            
            for idx, row in df.iterrows():
                data = {
                    'nama_paket': str(row['nama_paket'])[:500],
                    'pagu': float(row['pagu']) if pd.notna(row['pagu']) else 0,
                    'jenis': str(row['jenis']),
                    'tahun': int(row['tahun']) if pd.notna(row['tahun']) else datetime.now().year,
                    'kategori': str(row['kategori']),
                    'metode': str(row['metode']),
                    'bulan': str(row['bulan']),
                    'lokasi': str(row['lokasi']),
                    'instansi': str(row['instansi'])[:200],
                    'nomor_id': str(row['nomor_id']).strip()
                }
                
                success, message, is_duplicate = self.db_manager.insert_paket(data)
                
                if success:
                    if not is_duplicate:
                        new_records += 1
                    else:
                        duplicate_records += 1
                else:
                    errors.append(f"Row {idx+2}: {message}")
            
            status = "SUCCESS" if len(errors) < total_records else "PARTIAL"
            self.db_manager.log_upload(
                filename=filename,
                file_size=file_size,
                total_records=total_records,
                new_records=new_records,
                duplicate_records=duplicate_records,
                status=status,
                error_msg="; ".join(errors[:10]) if errors else None
            )
            
            return total_records, new_records, duplicate_records, errors
            
        except Exception as e:
            self.db_manager.log_upload(
                filename=filename,
                file_size=file_size,
                total_records=0,
                new_records=0,
                duplicate_records=0,
                status="FAILED",
                error_msg=str(e)
            )
            return 0, 0, 0, [str(e)]
    
    def _clean_data(self, df):
        if 'pagu' in df.columns:
            df['pagu'] = df['pagu'].astype(str).str.replace('.', '', regex=False)
            df['pagu'] = df['pagu'].str.replace(',', '.', regex=False)
            df['pagu'] = pd.to_numeric(df['pagu'], errors='coerce').fillna(0)
        
        if 'tahun' in df.columns:
            df['tahun'] = pd.to_numeric(df['tahun'], errors='coerce').fillna(2025).astype(int)
        
        text_columns = ['nama_paket', 'jenis', 'kategori', 'metode', 'bulan', 'lokasi', 'instansi']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        if 'nomor_id' in df.columns:
            df['nomor_id'] = df['nomor_id'].astype(str).str.strip()
            df = df.drop_duplicates(subset=['nomor_id'], keep='first')
        
        return df
