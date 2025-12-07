from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import cv2
import time
import math
from werkzeug.utils import secure_filename
import threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'speed_detection_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

processing_status = {
    'is_processing': False,
    'current_file': None,
    'progress': 0,
    'message': 'Ready to process'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video(input_path, output_path):
    global processing_status
    
    try:
        processing_status['is_processing'] = True
        processing_status['progress'] = 0
        processing_status['message'] = 'Starting video processing...'
        
        # Import and use the speed_detector functionality
        import subprocess
        import sys
        
        # Update progress
        processing_status['progress'] = 10
        processing_status['message'] = 'Initializing speed detection model...'
        
        # Run speed_detector.py with input and output paths
        script_path = os.path.join(os.path.dirname(__file__), 'speed_detector.py')
        
        # Start subprocess with real-time output monitoring
        process = subprocess.Popen([sys.executable, script_path, input_path, output_path], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Monitor progress based on output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output = output.strip()
                # Check for progress updates
                if output.startswith('PROGRESS:'):
                    try:
                        # Parse detailed progress like "PROGRESS:72/4164"
                        progress_data = output.split(':')[1]
                        if '/' in progress_data:
                            current_frame, total_frames = progress_data.split('/')
                            percentage = (int(current_frame) / int(total_frames)) * 80 + 10
                            processing_status['progress'] = min(percentage, 90)
                            processing_status['message'] = f'Processing frame {current_frame} of {total_frames}... {int(percentage)}%'
                        else:
                            # Fallback for simple percentage
                            progress_value = int(progress_data)
                            processing_status['progress'] = progress_value
                            processing_status['message'] = f'Processing video... {progress_value}%'
                    except:
                        pass
                elif 'Creating new tracker' in output:
                    processing_status['progress'] = min(processing_status['progress'] + 1, 80)
                    processing_status['message'] = f'Detecting and tracking vehicles... {processing_status["progress"]}%'
        
        # Get final result
        result = process.communicate()
        
        if process.returncode == 0:
            processing_status['progress'] = 100
            processing_status['message'] = 'Processing completed successfully! Speed detection applied to video.'
        else:
            raise Exception(f"Speed detection failed: {result[1]}")
        
    except subprocess.TimeoutExpired:
        processing_status['message'] = 'Error: Processing timed out. Please try with a shorter video.'
    except Exception as e:
        processing_status['message'] = f'Error: {str(e)}'
    finally:
        processing_status['is_processing'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return {'success': False, 'error': 'No file selected'}
        
        file = request.files['file']
        if file.filename == '':
            return {'success': False, 'error': 'No file selected'}
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_filename = f"output_{timestamp}.mp4"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            file.save(input_path)
            
            # Start processing in background thread
            processing_thread = threading.Thread(target=process_video, args=(input_path, output_path))
            processing_thread.start()
            
            processing_status['current_file'] = output_filename
            
            return {'success': True, 'message': 'File uploaded successfully! Processing started...'}
            
        else:
            return {'success': False, 'error': 'Invalid file type. Please upload MP4, AVI, MOV, or MKV files.'}
        
    except Exception as e:
        return {'success': False, 'error': f'Error uploading file: {str(e)}'}
        print(f"Upload error: {str(e)}")  # Debug print

@app.route('/status')
def get_status():
    return processing_status

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/outputs/<filename>')
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    # Production deployment
    app.run(debug=False, host='0.0.0.0', port=5000)
