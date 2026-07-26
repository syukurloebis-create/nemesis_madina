import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def process_file(self, filepath, original_filename):
        """Process uploaded file"""
        try:
            # Read file based on extension
            ext = original_filename.split('.')[-1].lower()
            
            if ext == 'csv':
                df = pd.read_csv(filepath, encoding='utf-8')
            elif ext in ['xlsx', 'xls']:
                df = pd.read_excel(filepath)
            else:
                return 0, 0, 0, [f"Unsupported file format: {ext}"]
            
            # Clean column names
            df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
            
            # Map columns to database fields
            column_mapping = {
                'nomor_id': ['nomor_id', 'id', 'no', 'nomor'],
                'tahun': ['tahun', 'year'],
                'jenis': ['jenis', 'type', 'kategori'],
                'instansi': ['instansi', 'agency', 'department'],
                'nama_paket': ['nama_paket', 'nama', 'paket', 'name'],
                'pagu': ['pagu', 'nilai', 'amount', 'value'],
                'sumber_dana': ['sumber_dana', 'sumber', 'funding'],
                'metode_pengadaan': ['metode_pengadaan', 'metode', 'method'],
                'status': ['status', 'state']
            }
            
            # Rename columns
            rename_dict = {}
            for target, sources in column_mapping.items():
                for source in sources:
                    if source in df.columns:
                        rename_dict[source] = target
                        break
            
            if rename_dict:
                df = df.rename(columns=rename_dict)
            
            # Required columns
            required = ['nomor_id', 'tahun', 'jenis', 'instansi']
            missing = [col for col in required if col not in df.columns]
            if missing:
                return 0, 0, 0, [f"Missing required columns: {missing}"]
            
            # Convert to records
            records = df.to_dict('records')
            
            # Insert data
            inserted = 0
            duplicates = 0
            errors = []
            
            for record in records:
                try:
                    # Ensure nomor_id is string
                    record['nomor_id'] = str(record['nomor_id'])
                    
                    # Convert pagu to float if exists
                    if 'pagu' in record and record['pagu']:
                        try:
                            record['pagu'] = float(record['pagu'])
                        except:
                            record['pagu'] = 0.0
                    
                    # Set default values for missing fields
                    for field in ['sumber_dana', 'metode_pengadaan', 'status']:
                        if field not in record:
                            record[field] = 'Unknown'
                    
                    success = self.db_manager.insert_data(record)
                    if success:
                        inserted += 1
                    else:
                        duplicates += 1
                except Exception as e:
                    errors.append(str(e)[:100])
                    duplicates += 1
            
            # Clean up
            os.remove(filepath)
            
            return len(records), inserted, duplicates, errors
            
        except Exception as e:
            logger.error(f"File processing error: {e}")
            return 0, 0, 0, [str(e)]
