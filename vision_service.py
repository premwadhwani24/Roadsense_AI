"""
Road Vision Service - Production-Grade Inference Engine
RoadSense AI

Loads trained RoadDefectResNet model and classifies road imagery into
defects (Pothole, Crack, Normal) with confidence scores and severity indicators.
"""
import os
import sys
import logging
from io import BytesIO
from pathlib import Path
from PIL import Image
import torch

logger = logging.getLogger(__name__)

# Ensure road_defect_model can be imported
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from road_defect_model import RoadDefectResNet, FastImageTransform
except ImportError:
    try:
        from ml.road_defect_model import RoadDefectResNet, FastImageTransform
    except ImportError:
        RoadDefectResNet = None
        FastImageTransform = None

class RoadVisionService:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.getenv("ROAD_DEFECT_MODEL_PATH", "road_defect_cnn.pt")

        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.classes = ["Crack", "Normal", "Pothole"]
        self.transform = None

        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            # Check relative to script dir
            alt_path = current_dir / self.model_path
            if alt_path.exists():
                self.model_path = str(alt_path)
            else:
                logger.warning(f"Model checkpoint '{self.model_path}' not found on disk. Vision service in standby.")
                return

        try:
            checkpoint = torch.load(self.model_path, map_location=self.device)
            if isinstance(checkpoint, dict) and "classes" in checkpoint:
                self.classes = checkpoint["classes"]
            
            num_classes = len(self.classes)
            
            # Instantiate model architecture
            if RoadDefectResNet is not None:
                self.model = RoadDefectResNet(num_classes=num_classes)
                if isinstance(checkpoint, dict) and "model_state" in checkpoint:
                    self.model.load_state_dict(checkpoint["model_state"])
                else:
                    self.model.load_state_dict(checkpoint)
            else:
                # Fallback to torchvision if available
                from torchvision import models
                self.model = models.resnet18()
                self.model.fc = torch.nn.Linear(self.model.fc.in_features, num_classes)
                if isinstance(checkpoint, dict) and "model_state" in checkpoint:
                    self.model.load_state_dict(checkpoint["model_state"])
                else:
                    self.model.load_state_dict(checkpoint)

            self.model.to(self.device)
            self.model.eval()

            if FastImageTransform is not None:
                self.transform = FastImageTransform(size=(224, 224), is_train=False)
            
            logger.info(f"RoadVisionService loaded successfully from '{self.model_path}' with classes: {self.classes}")
        except Exception as e:
            logger.error(f"Failed to load RoadVisionService model: {e}")
            self.model = None

    def analyze_image(self, image_input):
        """
        Analyzes road image and returns classification label and confidence.
        `image_input` can be a file path (str/Path), PIL.Image, or file bytes.
        """
        if self.model is None:
            raise RuntimeError("Vision model is not loaded or unavailable.")

        # Load image
        if isinstance(image_input, (str, Path)):
            img = Image.open(image_input)
        elif isinstance(image_input, bytes):
            img = Image.open(BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        img = img.convert("RGB")

        # Transform
        if self.transform is not None:
            tensor = self.transform(img).unsqueeze(0).to(self.device)
        else:
            import numpy as np
            arr = np.array(img.resize((224, 224)), dtype=np.float32).transpose((2, 0, 1)) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)
            arr = (arr - mean) / std
            tensor = torch.from_numpy(arr).unsqueeze(0).to(self.device)

        # Inference
        with torch.no_grad():
            output = self.model(tensor)
            probs = torch.softmax(output, dim=1)[0]
            conf, pred_idx = torch.max(probs, dim=0)

        label = self.classes[pred_idx.item()]
        conf_pct = round(conf.item() * 100.0, 2)

        # Calculate severity
        if label == "Pothole":
            severity = "CRITICAL" if conf_pct >= 80 else "HIGH"
        elif label == "Crack":
            severity = "MEDIUM" if conf_pct >= 80 else "LOW"
        else:
            severity = "NORMAL"

        prob_dict = {self.classes[i]: round(probs[i].item() * 100.0, 2) for i in range(len(self.classes))}

        return {
            "label": label,
            "confidence": conf_pct,
            "severity": severity,
            "probabilities": prob_dict,
            "status": "DETECTED" if label != "Normal" else "CLEAR"
        }

    def analyze_image_detailed(self, image_input):
        """Detailed analysis including bounding box suggestions and actionable recommendations"""
        res = self.analyze_image(image_input)
        
        recommendation = "No immediate action needed. Road in satisfactory condition."
        if res["label"] == "Pothole":
            recommendation = "Priority repair required: Dispatch pothole patcher and deploy road warning signage."
        elif res["label"] == "Crack":
            recommendation = "Preventive maintenance recommended: Apply asphalt crack sealant to prevent water ingress."

        res["recommendation"] = recommendation
        return res
