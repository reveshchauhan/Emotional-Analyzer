import os
import cv2
import numpy as np
import base64
from datetime import datetime
import json
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import EmotionResult
from emotion_detector import EmotionDetector

# Initialize emotion detector
emotion_detector = EmotionDetector()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    # Get emotion statistics
    emotion_stats = db.session.query(
        EmotionResult.dominant_emotion, 
        db.func.count(EmotionResult.id)
    ).group_by(EmotionResult.dominant_emotion).all()
    
    # Format the data for the chart
    emotions = [stat[0] for stat in emotion_stats]
    counts = [stat[1] for stat in emotion_stats]
    
    # Get recent results
    recent_results = EmotionResult.query.order_by(EmotionResult.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          emotions=json.dumps(emotions), 
                          counts=json.dumps(counts),
                          recent_results=recent_results)

@app.route('/history')
def history():
    """Show history of emotion detections"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get paginated results
    results = EmotionResult.query.order_by(EmotionResult.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html', results=results)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image upload and process it for emotion detection"""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to make filename unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read the image
            image = cv2.imread(filepath)
            if image is None:
                flash('Error reading the image', 'error')
                return redirect(request.url)
            
            # Detect emotions
            results = emotion_detector.detect_emotions(image)
            
            if not results:
                flash('No faces detected in the image', 'warning')
                return redirect(request.url)
            
            # Draw emotions on the image
            annotated_image = emotion_detector.draw_emotions(image, results)
            
            # Save the annotated image
            annotated_filename = f"annotated_{filename}"
            annotated_filepath = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            cv2.imwrite(annotated_filepath, annotated_image)
            
            # Save results to database
            for result in results:
                emotion_result = EmotionResult(
                    filename=annotated_filename,
                    source_type='upload',
                    emotions=result['emotions'],
                    dominant_emotion=result['dominant_emotion'],
                    confidence=result['confidence'],
                    faces_detected=len(results)
                )
                db.session.add(emotion_result)
            
            db.session.commit()
            flash('Emotion detection completed successfully!', 'success')
            
            # Redirect to history page
            return redirect(url_for('history'))
            
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(request.url)
    else:
        flash('Invalid file type. Please upload an image (png, jpg, jpeg)', 'error')
        return redirect(request.url)

@app.route('/webcam', methods=['POST'])
def process_webcam():
    """Process webcam image for emotion detection"""
    try:
        # Get the image data from the request
        image_data = request.form.get('image')
        if not image_data:
            return jsonify({'error': 'No image data received'}), 400
        
        # Remove the data URL prefix
        if 'data:image' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({'error': 'Could not decode image'}), 400
        
        # Detect emotions
        results = emotion_detector.detect_emotions(image)
        
        if not results:
            return jsonify({'error': 'No faces detected'}), 404
        
        # Draw emotions on the image
        annotated_image = emotion_detector.draw_emotions(image, results)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webcam_{timestamp}.jpg"
        
        # Save the annotated image
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filepath, annotated_image)
        
        # Save results to database
        for result in results:
            emotion_result = EmotionResult(
                filename=filename,
                source_type='webcam',
                emotions=result['emotions'],
                dominant_emotion=result['dominant_emotion'],
                confidence=result['confidence'],
                faces_detected=len(results)
            )
            db.session.add(emotion_result)
        
        db.session.commit()
        
        # Return the results
        response = {
            'success': True,
            'results': [{
                'dominant_emotion': r['dominant_emotion'],
                'confidence': r['confidence'],
                'emotions': r['emotions']
            } for r in results],
            'image_url': url_for('uploaded_file', filename=filename)
        }
        
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error processing webcam image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/emotion-stats')
def emotion_stats():
    """Get emotion statistics for the dashboard"""
    # Get emotion statistics
    emotion_stats = db.session.query(
        EmotionResult.dominant_emotion, 
        db.func.count(EmotionResult.id)
    ).group_by(EmotionResult.dominant_emotion).all()
    
    # Format the data
    stats = {stat[0]: stat[1] for stat in emotion_stats}
    
    return jsonify(stats)
