from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
ML_API_URL = 'http://localhost:5001'
PROCESSED_DATA_DIR = 'data/processed'

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/health')
def check_system_health():
    """Check health of all system components"""
    health_status = {
        'ml_api': check_ml_api_health(),
        'data_files': check_data_files(),
        'recent_metrics': get_recent_metrics()
    }
    return jsonify(health_status)

@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    """Revenue prediction page"""
    if request.method == 'POST':
        # Get form data
        data = {
            'quantity': int(request.form['quantity']),
            'unit_price': float(request.form['unit_price']),
            'hour': int(request.form.get('hour', 14)),
            'day_of_week': int(request.form.get('day_of_week', 2)),
            'country': request.form.get('country', 'United Kingdom')
        }
        
        # Call ML API
        try:
            response = requests.post(f'{ML_API_URL}/predict', json=data, timeout=5)
            if response.status_code == 200:
                prediction_result = response.json()
                return render_template('predict.html', 
                                     prediction=prediction_result, 
                                     input_data=data)
            else:
                error = f"API Error: {response.status_code}"
                return render_template('predict.html', error=error)
        except Exception as e:
            error = f"Connection Error: {str(e)}"
            return render_template('predict.html', error=error)
    
    return render_template('predict.html')

@app.route('/metrics')
def metrics_page():
    """Business metrics page"""
    try:
        metrics = load_latest_metrics()
        return render_template('metrics.html', metrics=metrics)
    except Exception as e:
        return render_template('metrics.html', error=str(e))

@app.route('/monitoring')
def monitoring_page():
    """System monitoring page"""
    return render_template('monitoring.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for predictions"""
    try:
        data = request.json
        response = requests.post(f'{ML_API_URL}/predict', json=data, timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def check_ml_api_health():
    """Check if ML API is running"""
    try:
        response = requests.get(f'{ML_API_URL}/health', timeout=5)
        return {
            'status': 'healthy' if response.status_code == 200 else 'error',
            'response_time': response.elapsed.total_seconds()
        }
    except Exception as e:
        return {'status': 'offline', 'error': str(e)}

def check_data_files():
    """Check data file status"""
    files = {
        'raw_data': Path('data/OnlineRetail.csv').exists(),
        'processed_data': Path(PROCESSED_DATA_DIR).exists(),
        'ml_model': Path('src/ml/revenue_model.pkl').exists()
    }
    return files

def get_recent_metrics():
    """Get recent business metrics"""
    try:
        processed_dir = Path(PROCESSED_DATA_DIR)
        if processed_dir.exists():
            json_files = list(processed_dir.glob('*.json'))
            if json_files:
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    return json.load(f)
    except Exception as e:
        pass
    return None

def load_latest_metrics():
    """Load latest business metrics"""
    processed_dir = Path(PROCESSED_DATA_DIR)
    if not processed_dir.exists():
        raise Exception("No processed data directory found")
    
    json_files = list(processed_dir.glob('*.json'))
    if not json_files:
        raise Exception("No metrics files found")
    
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    with open(latest_file, 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('src/dashboard/templates').mkdir(parents=True, exist_ok=True)
    Path('src/dashboard/static').mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting E-commerce Analytics Dashboard")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔗 Make sure ML API is running at: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5002, debug=True)