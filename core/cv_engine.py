import os
import cv2
import numpy as np
import time

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

class CVEngine:
    def __init__(self, weights_path='yolov8n.pt'):
        self.weights_path = weights_path
        self.model = None
        self.load_model(self.weights_path)
    
    def load_model(self, path):
        if not YOLO:
            print("WARNING: ultralytics is not installed. Inference will be mocked.")
            return
        try:
            if not os.path.exists(path) and path != 'yolov8n.pt':
                 print(f"Weights {path} not found. Falling back to default YOLOv8n.")
                 self.model = YOLO('yolov8n.pt')
            else:
                 self.model = YOLO(path)
            print(f"Model {path} loaded successfully.")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None

    def infer(self, image_bytes):
        """
        Runs YOLO inference on an image bytes array.
        Returns a list of dicts: [{'class_name': str, 'confidence': float}]
        """
        if not self.model:
            # Note: For prototype testing without a trained model or if ultralytics fails,
            # we can inject a mock detection if the user uploads any image.
            # In a real app we simply return []
            return [{"class_name": "mock_product", "confidence": 0.99}]

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []
            
        results = self.model.predict(img, conf=0.5, verbose=False)
        
        detected = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls_id]
                detected.append({
                    'class_name': class_name,
                    'confidence': conf
                })
        return detected

cv_engine = CVEngine()
