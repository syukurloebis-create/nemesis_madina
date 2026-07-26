from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
import os
import pandas as pd
from werkzeug.utils import secure_filename
from database import DatabaseManager
from file_processor import FileProcessor
import json
import time
from functools import wraps
from datetime import datetime, timedelta
import hashlib
import logging
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# ============================================
# FIX: Custom JSON encoder untuk numpy/pandas
# ============================================
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Buat folder upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inisialisasi database
try:
    db_manager = DatabaseManager()
    file_processor = FileProcessor(db_manager)
    logger.info("Database and FileProcessor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize: {e}")
    db_manager = None
    file_processor = None

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# ============================================
# CACHE IMPLEMENTATION
# ============================================
class Cache:
    def __init__(self):
        self._cache = {}
        self._ttl = {}
        self._hits = 0
        self._misses = 0
    
    def get(self, key):
        if key in self._cache:
            if time.time() < self._ttl.get(key, 0):
                self._hits += 1
                return self._cache[key]
            else:
                del self._cache[key]
                del self._ttl[key]
        self._misses += 1
        return None
    
    def set(self, key, value, ttl=60):
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl
    
    def clear(self):
        self._cache.clear()
        self._ttl.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self):
        total = self._hits + self._misses
        return {
            'size': len(self._cache),
            'hits': self._hits,
            'misses': self._misses,
            'hit_ratio': self._hits / total if total > 0 else 0
        }

cache = Cache()

# ============================================
# CACHE DECORATOR
# ============================================
def cache_response(ttl=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            key = hashlib.md5(key.encode()).hexdigest()
            
            cached = cache.get(key)
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            
            if isinstance(result, (dict, list)) or hasattr(result, 'get_data'):
                cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

# ============================================
# MIDDLEWARE
# ============================================
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = (time.time() - request.start_time) * 1000
        response.headers['X-Response-Time'] = f"{duration:.2f}ms"
        
        if duration > 1000:
            logger.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}ms")
    
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'public, max-age=60'
        response.headers['Vary'] = 'Accept-Encoding'
    
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

# ============================================
# ROUTES
# ============================================
@app.route('/health')
def health_check():
    status = {
        'status': 'healthy',
        'service': 'nemesis-api',
        'version': '8.0.0',
        'timestamp': datetime.now().isoformat(),
        'cache': cache.get_stats(),
        'database': 'connected' if db_manager else 'not_initialized'
    }
    return jsonify(status)

@app.route('/api/cache/stats')
def cache_stats():
    return jsonify(cache.get_stats())

@app.route('/api/cache/clear', methods=['POST'])
def cache_clear():
    cache.clear()
    return jsonify({'success': True, 'message': 'Cache cleared'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if not db_manager:
        return render_template('index.html', stats={'total_records': 0})
    stats = db_manager.get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not db_manager or not file_processor:
        flash('System not initialized properly', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file format.', 'error')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
        file.save(filepath)
        
        try:
            total, new_records, duplicate_records, errors = file_processor.process_file(filepath, filename)
            cache.clear()
            
            if total > 0:
                flash(f'Upload completed! Total: {total}, New: {new_records}, Duplicate: {duplicate_records}', 'success')
                if errors:
                    flash(f'Warnings: {len(errors)} issues', 'warning')
            else:
                flash(f'Upload failed', 'error')
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            flash(f'Error: {str(e)}', 'error')
        
        return redirect(url_for('upload'))
    
    return render_template('upload.html')

@app.route('/data')
@cache_response(ttl=30)
def view_data():
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
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
    conn.close()
    
    return render_template('data.html', 
                         data=data, 
                         page=page, 
                         total_pages=total_pages,
                         total_records=total_records,
                         per_page=per_page,
                         filters=filters,
                         years=years,
                         types=types)

@app.route('/dashboard')
@cache_response(ttl=60)
def dashboard():
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    stats = db_manager.get_statistics()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/stats')
@cache_response(ttl=30)
def api_stats():
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    stats = db_manager.get_statistics()
    return jsonify(stats)

@app.route('/api/delete/<nomor_id>', methods=['DELETE'])
def api_delete(nomor_id):
    if not db_manager:
        return jsonify({'success': False, 'message': 'Database not initialized'}), 500
    
    success = db_manager.delete_data(nomor_id)
    if success:
        cache.clear()
        return jsonify({'success': True, 'message': 'Data deleted'})
    return jsonify({'success': False, 'message': 'Data not found'}), 404

@app.route('/export')
def export_data():
    if not db_manager:
        return jsonify({'error': 'Database not initialized'}), 500
    
    df = db_manager.get_all_data(limit=10000, offset=0)
    response = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    return Response(
        response,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=rup_data_export.csv'}
    )

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting NEMESIS API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
