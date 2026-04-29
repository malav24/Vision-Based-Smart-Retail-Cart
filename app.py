import os
import uuid
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from config import SECRET_KEY, UPLOAD_FOLDER, DATASET_FOLDER
from core.db import query_db, insert_db
from core.cv_engine import cv_engine
from core.utils import check_cooldown
from core.trainer import trainer
from werkzeug.security import check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = SECRET_KEY

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATASET_FOLDER, exist_ok=True)

# ===== Admin Routes =====
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = query_db("SELECT * FROM admins WHERE username = ?", [username], one=True)
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/login.html', error="Invalid Credentials")
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    stats = {
        'total_sales': query_db("SELECT SUM(total_amount) as total FROM billing_sessions WHERE status='completed'", one=True)['total'] or 0,
        'products_count': query_db("SELECT COUNT(*) as count FROM products", one=True)['count'] or 0
    }
    recent_sessions = query_db("SELECT * FROM billing_sessions ORDER BY start_time DESC LIMIT 5")
    return render_template('admin/dashboard.html', stats=stats, recent_sessions=recent_sessions)

@app.route('/admin/products', methods=['GET'])
def admin_products():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    products = query_db("SELECT * FROM products")
    return render_template('admin/products.html', products=products)

@app.route('/api/products', methods=['POST'])
def add_product():
    if not session.get('admin_logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    data = request.form
    try:
        product_id = insert_db(
            "INSERT INTO products (product_name, sku, category, price, stock, model_class_name) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['sku'], data['category'], float(data['price']), int(data['stock']), data['model_class_name'])
        )
        return jsonify({'success': True, 'product_id': product_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/training')
def admin_training():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login'))
    jobs = query_db("SELECT * FROM training_jobs ORDER BY start_time DESC LIMIT 10")
    classes = query_db("SELECT model_class_name FROM products")
    models = query_db("SELECT * FROM model_versions")
    return render_template('admin/training.html', jobs=jobs, classes=classes, models=models)

@app.route('/api/training/upload', methods=['POST'])
def upload_dataset():
    if not session.get('admin_logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    if 'dataset' not in request.files: return jsonify({'error': 'No file provided'}), 400
    file = request.files['dataset']
    if not file.filename.endswith('.zip'): return jsonify({'error': 'Please upload a .zip file (Roboflow format)'}), 400

    filename = f"dataset_{uuid.uuid4().hex}.zip"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    success, msg = trainer.extract_dataset(filepath)
    if success:
        classes = trainer.parse_classes()
        return jsonify({'success': True, 'msg': msg, 'classes': classes})
    return jsonify({'error': msg}), 500

@app.route('/api/training/start', methods=['POST'])
def start_training():
    if not session.get('admin_logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    epochs = int(data.get('epochs', 20))
    try:
        job_id = insert_db("INSERT INTO training_jobs (status) VALUES ('pending')")
        trainer.start_training(job_id=job_id, epochs=epochs)
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== Dropbox Routes =====
@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/dropbox')
def dropbox_index():
    return render_template('dropbox/index.html')

@app.route('/api/dropbox/infer', methods=['POST'])
def dropbox_infer():
    if 'image' not in request.files: return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    img_bytes = file.read()
    
    detected = cv_engine.infer(img_bytes)
    if not detected:
        return jsonify({'success': True, 'items': []})
        
    valid_items = []
    for item in detected:
        if item['confidence'] < 0.6: continue
        product = query_db("SELECT * FROM products where model_class_name = ?", [item['class_name']], one=True)
        if product:
            if check_cooldown(product['product_id']):
                valid_items.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'price': product['price']
                })
    return jsonify({'success': True, 'items': valid_items})

@app.route('/api/dropbox/cart/clear', methods=['POST'])
def clear_cart():
    # Frontend handles clear, backend just acknowledges
    return jsonify({'success': True})

@app.route('/api/dropbox/checkout', methods=['POST'])
def process_checkout():
    data = request.json
    cart = data.get('cart', [])
    if not cart: return jsonify({'error': 'Cart is empty'}), 400
    try:
        session_id = insert_db("INSERT INTO billing_sessions (status) VALUES ('completed')")
        total = 0.0
        for item in cart:
            total += float(item['price'])
            insert_db("INSERT INTO billing_items (session_id, product_id, price_at_time) VALUES (?, ?, ?)", (session_id, item['id'], item['price']))
            query_db("UPDATE products SET stock = stock - 1 WHERE product_id = ?", [item['id']])
        query_db("UPDATE billing_sessions SET total_amount = ? WHERE session_id = ?", [total, session_id])
        return jsonify({'success': True, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== Mobile Camera Routes =====
@app.route('/mobile/camera')
def mobile_camera():
    """iPhone camera interface for real-time object detection"""
    return render_template('dropbox/mobile_camera.html')

@app.route('/api/mobile/detect', methods=['POST'])
def mobile_detect():
    """Process frame from iPhone camera and detect items"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    try:
        file = request.files['image']
        img_bytes = file.read()
        
        # Run YOLO inference
        detected = cv_engine.infer(img_bytes)
        
        if not detected:
            return jsonify({'success': True, 'items': []})
        
        # Filter and map detections to products
        valid_items = []
        for item in detected:
            if item['confidence'] < 0.5:  # Lower threshold for mobile
                continue
            
            # Query product database for matching class
            product = query_db(
                "SELECT * FROM products WHERE model_class_name = ?", 
                [item['class_name']], 
                one=True
            )
            
            if product:
                # Check cooldown to avoid duplicate detections
                if check_cooldown(product['product_id']):
                    valid_items.append({
                        'product_id': product['product_id'],
                        'product_name': product['product_name'],
                        'price': float(product['price']),
                        'confidence': float(item['confidence']),
                        'class_name': item['class_name']
                    })
                    
                    # Log detection in database
                    insert_db(
                        "INSERT INTO detection_logs (detected_class, confidence, timestamp) VALUES (?, ?, ?)",
                        (item['class_name'], float(item['confidence']), datetime.now())
                    )
        
        return jsonify({'success': True, 'items': valid_items})
        
    except Exception as e:
        print(f"Error in mobile_detect: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Disable reloader so file uploads don't cause the server to crash halfway
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
