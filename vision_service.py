import torch
from torchvision import models, transforms
from PIL import Image

class RoadVisionService:
    def __init__(self):
        checkpoint = torch.load("road_defect_cnn.pt", map_location="cpu")
        self.classes = checkpoint["classes"]

        self.model = models.resnet18()
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, len(self.classes))
        self.model.load_state_dict(checkpoint["model_state"])
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor()
        ])

    def analyze_image(self, image_path):
        img = Image.open(image_path).convert("RGB")
        img = self.transform(img).unsqueeze(0)

        with torch.no_grad():
            output = self.model(img)
            prob = torch.softmax(output, dim=1)
            conf, pred = torch.max(prob, 1)

        return {
            "label": self.classes[pred.item()],
            "confidence": round(conf.item() * 100, 2)
        }
