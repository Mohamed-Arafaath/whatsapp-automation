from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import uuid
from whatsapp_service import WhatsAppService

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

# Ensure upload directory exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store active services: session_id -> WhatsAppService
services = {}

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal Server Error: ' + str(error)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

def get_service():
    """Get or create WhatsApp service for current session."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    
    if session_id not in services:
        services[session_id] = WhatsAppService(session_id)
    
    return services[session_id]

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle Excel file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            # Read file into memory
            file_content = file.read()
            
            service = get_service()
            success = service.load_contacts(file_content)
            
            if success:
                return jsonify({
                    'success': True, 
                    'total_contacts': len(service.contacts_df)
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to parse Excel file'}), 400
                
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/connect', methods=['POST'])
def connect():
    """Initialize WhatsApp Web connection."""
    try:
        service = get_service()
        service.setup_driver()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/qr', methods=['GET'])
def get_qr():
    """Get QR code for WhatsApp login."""
    try:
        service = get_service()
        qr_data = service.get_qr_code()
        
        if qr_data:
            return jsonify({'success': True, 'qr_code': qr_data})
        else:
            return jsonify({'success': False, 'error': 'QR code not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/check_connection', methods=['GET'])
def check_connection():
    """Check if WhatsApp is connected."""
    try:
        service = get_service()
        connected = service.check_connection()
        return jsonify({'success': True, 'connected': connected})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/start', methods=['POST'])
def start():
    """Start sending messages."""
    try:
        data = request.json
        message = data.get('message', '')
        count = int(data.get('count', 0))
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        if count <= 0:
            return jsonify({'success': False, 'error': 'Invalid contact count'}), 400
        
        service = get_service()
        
        if not service.is_connected:
            return jsonify({'success': False, 'error': 'WhatsApp not connected'}), 400
        
        if service.is_running:
            return jsonify({'success': False, 'error': 'Already running'}), 400
        
        service.start_sending(message, count)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop():
    """Stop sending messages."""
    try:
        service = get_service()
        service.stop_sending()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/disconnect', methods=['POST'])
def disconnect():
    """Disconnect WhatsApp and close browser."""
    try:
        service = get_service()
        service.close()
        service.is_connected = False
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get current status."""
    try:
        service = get_service()
        status_data = service.get_status()
        return jsonify({'success': True, 'status': status_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('whatsapp_sessions', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    print("\n" + "="*60)
    print("WhatsApp Cold Messaging Web App")
    print("="*60)
    print("\n🌐 Server starting at: http://localhost:5001")
    print("📱 Open this URL in your browser to use the app\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
