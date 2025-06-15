# setup_dashboard.py
"""
Setup script to create the Flask Dashboard UI for the E-commerce Analytics project
"""

import os
from pathlib import Path

def create_dashboard_structure():
    """Create the necessary directory structure for the dashboard"""
    
    print("🚀 Setting up Flask Dashboard UI...")
    print("=" * 50)
    
    # Create dashboard directory structure
    dashboard_dirs = [
        'src/dashboard',
        'src/dashboard/templates',
        'src/dashboard/static',
        'src/dashboard/static/css',
        'src/dashboard/static/js'
    ]
    
    for dir_path in dashboard_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    # Create the main dashboard app file
    dashboard_app_content = '''# src/dashboard/dashboard_app.py
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
    print("🚀 Starting E-commerce Analytics Dashboard")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔗 Make sure ML API is running at: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
'''
    
    # Write the dashboard app file
    with open('src/dashboard/dashboard_app.py', 'w') as f:
        f.write(dashboard_app_content)
    print("✅ Created: src/dashboard/dashboard_app.py")
    
    # Create HTML templates (you'll need to copy the HTML from the artifacts)
    print("\n📝 HTML Template Files Needed:")
    print("   Create these files in src/dashboard/templates/:")
    print("   1. dashboard.html - Main dashboard page")
    print("   2. predict.html - Prediction page")  
    print("   3. metrics.html - Business metrics page")
    print("   4. monitoring.html - System monitoring page")
    
    # Create a basic requirements addition
    dashboard_requirements = '''
# Additional requirements for Flask Dashboard
Flask==2.3.3
requests==2.32.4
'''
    
    print(f"\n📦 Additional Python Requirements:")
    print("   Add these to your requirements.txt:")
    print(dashboard_requirements)
    
    # Create startup instructions
    startup_instructions = '''
# How to start the Flask Dashboard

## 1. Install requirements:
pip install Flask requests

## 2. Start the ML API (in one terminal):
cd your-project-directory
python src/ml/prediction_api.py

## 3. Start the Dashboard (in another terminal):
cd your-project-directory  
python src/dashboard/dashboard_app.py

## 4. Access the dashboard:
Open your browser to: http://localhost:5000

## Dashboard Features:
- 🏠 Main Dashboard: System overview and navigation
- 🤖 Predictions: Interactive ML revenue predictions
- 📊 Metrics: Business analytics and KPIs
- 🖥️ Monitoring: Real-time system health monitoring

## Troubleshooting:
- Make sure both Flask and requests are installed
- Ensure the ML API is running on port 5001
- Check that your data files exist in data/ directory
- Run batch processing to generate metrics: python src/batch/daily_processor.py
'''
    
    with open('DASHBOARD_INSTRUCTIONS.md', 'w') as f:
        f.write(startup_instructions)
    print("✅ Created: DASHBOARD_INSTRUCTIONS.md")
    
    print(f"\n🎉 Dashboard setup complete!")
    print(f"\n📋 Next Steps:")
    print(f"1. Copy the HTML templates from the provided artifacts")
    print(f"2. Install Flask: pip install Flask requests")
    print(f"3. Start ML API: python src/ml/prediction_api.py")  
    print(f"4. Start Dashboard: python src/dashboard/dashboard_app.py")
    print(f"5. Open browser to: http://localhost:5000")

def create_quick_start_script():
    """Create a quick start script"""
    
    quick_start_content = '''#!/bin/bash
# quick_start_dashboard.sh
echo "🚀 Starting E-commerce Analytics Dashboard"
echo "========================================"

echo "1. Checking requirements..."
python3 -c "import flask, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing requirements. Installing..."
    pip install Flask requests
fi

echo "2. Starting ML API in background..."
python3 src/ml/prediction_api.py &
ML_PID=$!
sleep 3

echo "3. Starting Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:5000"
echo "🤖 ML API running at: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both services"

# Start dashboard
python3 src/dashboard/dashboard_app.py

# Cleanup on exit
kill $ML_PID 2>/dev/null
echo "🛑 Services stopped"
'''
    
    with open('quick_start_dashboard.sh', 'w') as f:
        f.write(quick_start_content)
    
    # Make it executable
    os.chmod('quick_start_dashboard.sh', 0o755)
    print("✅ Created: quick_start_dashboard.sh (executable)")

if __name__ == "__main__":
    create_dashboard_structure()
    create_quick_start_script()
    
    print(f"\n🏁 Setup Complete!")
    print(f"Read DASHBOARD_INSTRUCTIONS.md for detailed setup steps")