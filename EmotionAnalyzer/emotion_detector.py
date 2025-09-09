import cv2
import numpy as np
import os
import logging
from datetime import datetime

# Emotion labels
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detector with pre-trained models"""
        # Paths to pre-trained models
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Haar cascade for face detection
        self.face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        
        try:
            # Load the face detector
            self.face_detector = cv2.CascadeClassifier(self.face_cascade_path)
            logging.info("Loaded face detector successfully")
        except Exception as e:
            logging.error(f"Error loading face detector: {e}")
            raise
        
        # Download emotion model if needed (using a simplified mobilenet model)
        self.emotion_model = self._load_emotion_model()
    
    def _load_emotion_model(self):
        """Load or initialize a pre-trained emotion recognition model"""
        try:
            # For this implementation, we're using a more simplified approach with OpenCV DNN
            # In a real application, you might want to use a more sophisticated model
            # such as fer2013 or DeepFace
            
            # Since we can't actually download models here, we'll simulate with a dummy model
            # that returns random results (in a real implementation, you would use a proper model)
            class DummyEmotionModel:
                def predict(self, face):
                    # This is a placeholder. In a real app, you'd use a proper model.
                    # For demonstration, we'll generate random emotion probabilities
                    # In production, replace this with an actual model
                    probs = np.random.rand(len(EMOTIONS))
                    # Normalize to sum to 1
                    probs = probs / np.sum(probs)
                    return probs
            
            logging.info("Emotion model initialized")
            return DummyEmotionModel()
        except Exception as e:
            logging.error(f"Error loading emotion model: {e}")
            raise
    
    def detect_emotions(self, image):
        """
        Detect faces in the image and predict emotions
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            results: List of dictionaries containing face locations and emotions
        """
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        results = []
        
        # Process each face
        for (x, y, w, h) in faces:
            # Extract face ROI
            face_roi = gray[y:y+h, x:x+w]
            
            # Resize the face to the input size expected by the emotion model
            face_roi = cv2.resize(face_roi, (48, 48))
            
            # Normalize the face image
            face_roi = face_roi / 255.0
            
            # Reshape for the model
            face_roi = np.reshape(face_roi, (1, 48, 48, 1))
            
            # Predict emotions
            emotion_probs = self.emotion_model.predict(face_roi)
            
            # Get the dominant emotion
            emotion_idx = np.argmax(emotion_probs)
            emotion = EMOTIONS[emotion_idx]
            confidence = float(emotion_probs[emotion_idx])
            
            # Create emotion dictionary
            emotion_dict = {
                'box': (x, y, w, h),
                'emotions': {emotion: float(prob) for emotion, prob in zip(EMOTIONS, emotion_probs)},
                'dominant_emotion': emotion,
                'confidence': confidence
            }
            
            results.append(emotion_dict)
        
        return results
    
    def draw_emotions(self, image, results):
        """
        Draw bounding boxes and emotion labels on the image
        
        Args:
            image: Input image
            results: Detection results
            
        Returns:
            image: Annotated image
        """
        # Create a copy of the image
        annotated_image = image.copy()
        
        # Draw each face and its emotion
        for result in results:
            x, y, w, h = result['box']
            emotion = result['dominant_emotion']
            confidence = result['confidence']
            
            # Define color based on emotion
            colors = {
                'angry': (0, 0, 255),     # Red
                'disgust': (0, 128, 0),   # Green
                'fear': (255, 0, 255),    # Magenta
                'happy': (0, 255, 255),   # Yellow
                'sad': (255, 0, 0),       # Blue
                'surprise': (128, 0, 128), # Purple
                'neutral': (128, 128, 128) # Gray
            }
            color = colors.get(emotion, (255, 255, 255))
            # Draw bounding box
            cv2.rectangle(annotated_image, (x, y), (x+w, y+h), color, 2) 
            # Draw background for text
            cv2.rectangle(annotated_image, (x, y-40), (x+w, y), color, -1) 
            # Add emotion text
            text = f"{emotion}: {confidence:.2f}"
            cv2.putText(annotated_image, text, (x+5, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return annotated_image
