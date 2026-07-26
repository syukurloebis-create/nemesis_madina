from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import pandas as pd
from werkzeug.utils import secure_filename
from database import DatabaseManager
from file_processor import FileProcessor
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Buat folder upload jika belum ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inisialisasi database dan processor
db_manager = DatabaseManager()
file_processor = FileProcessor(db_manager)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Halaman utama dengan statistik ringkas"""
    stats = db_manager.get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Halaman upload file"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file format. Please upload CSV or Excel file.', 'error')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        try:
            total, new_records, duplicate_records, errors = file_processor.process_file(filepath, filename)
            
            if total > 0:
                flash(f'Upload completed! Total: {total}, New: {new_records}, Duplicate: {duplicate_records}', 'success')
                if errors:
                    flash(f'Warnings/Errors: {len(errors)} issues found', 'warning')
                    session['upload_errors'] = errors[:20]
            else:
                flash(f'Upload failed: {errors[0] if errors else "Unknown error"}', 'error')
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
        
        return redirect(url_for('upload'))
    
    upload_errors = session.pop('upload_errors', [])
    return render_template('upload.html', errors=upload_errors)

@app.route('/data')
def view_data():
    """Halaman untuk melihat data"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    filters = {
        'tahun': request.args.get('tahun', type=int),
        'jenis': request.args.get('jenis'),
        'instansi': request.args.get('instansi'),
        'search': request.args.get('search')
    }
    filters = {k: v for k, v in filters.items() if v}
    
    offset = (page - 1) * per_page
    df = db_manager.get_all_data(limit=per_page, offset=offset, filters=filters)
    total_records = db_manager.get_total_count(filters)
    total_pages = (total_records + per_page - 1) // per_page
    
    data = df.to_dict('records') if len(df) > 0 else []
    
    conn = db_manager.get_connection()
    years = pd.read_sql_query("SELECT DISTINCT tahun FROM rup_paket ORDER BY tahun DESC", conn)['tahun'].tolist()
    types = pd.read_sql_query("SELECT DISTINCT jenis FROM rup_paket ORDER BY jenis", conn)['jenis'].tolist()
    instansi_list = pd.read_sql_query("SELECT DISTINCT instansi FROM rup_paket ORDER BY instansi LIMIT 50", conn)['instansi'].tolist()
    conn.close()
    
    return render_template('data.html', 
                         data=data, 
                         page=page, 
                         total_pages=total_pages,
                         total_records=total_records,
                         per_page=per_page,
                         filters=filters,
                         years=years,
                         types=types,
                         instansi_list=instansi_list)

@app.route('/dashboard')
def dashboard():
    """Halaman dashboard dengan visualisasi data"""
    stats = db_manager.get_statistics()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    stats = db_manager.get_statistics()
    return jsonify(stats)

@app.route('/api/delete/<nomor_id>', methods=['DELETE'])
def api_delete(nomor_id):
    success = db_manager.delete_data(nomor_id)
    if success:
        return jsonify({'success': True, 'message': 'Data deleted successfully'})
    return jsonify({'success': False, 'message': 'Data not found'}), 404

@app.route('/export')
def export_data():
    df = db_manager.get_all_data(limit=10000, offset=0)
    response = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    from flask import Response
    return Response(
        response,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=rup_data_export.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
