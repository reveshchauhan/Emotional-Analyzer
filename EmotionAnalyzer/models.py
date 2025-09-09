from datetime import datetime
from app import db
import json

class EmotionResult(db.Model):
    """Model to store emotion detection results"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255))
    source_type = db.Column(db.String(20))  # 'upload' or 'webcam'
    
    # Store emotions as JSON string
    emotions_json = db.Column(db.Text)
    
    @property
    def emotions(self):
        """Convert JSON string to dictionary"""
        if self.emotions_json:
            return json.loads(self.emotions_json)
        return {}
    
    @emotions.setter
    def emotions(self, value):
        """Convert dictionary to JSON string"""
        self.emotions_json = json.dumps(value)
    
    # Store the dominant emotion
    dominant_emotion = db.Column(db.String(50))
    
    # Store the confidence score for the dominant emotion
    confidence = db.Column(db.Float)
    
    # Number of faces detected
    faces_detected = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<EmotionResult {self.id} {self.dominant_emotion} {self.confidence:.2f}>'
