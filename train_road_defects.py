"""
Train Road Defect Classification Model (ResNet-18)
RoadSense AI - Production Pipeline

Trains a 3-class defect classifier (Pothole, Crack, Normal) using
the Cracks and Potholes dataset with data augmentation, train/validation split,
and evaluation metrics.
"""
import os
import sys
import time
import argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from pathlib import Path

# Try to import our local road_defect_model
try:
    from road_defect_model import RoadDefectResNet, FastImageTransform
except ImportError:
    # If in different directory, add to sys.path
    current_dir = Path(__file__).resolve().parent
    sys.path.append(str(current_dir))
    from road_defect_model import RoadDefectResNet, FastImageTransform

class RoadDefectDataset(Dataset):
    """PyTorch Dataset loading road images from dataset_manifest.csv"""
    def __init__(self, manifest_df, split="train", transform=None):
        self.df = manifest_df[manifest_df["split"] == split].reset_index(drop=True)
        self.transform = transform
        self.classes = ["Crack", "Normal", "Pothole"]
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = row["image_path"]
        label_str = row["label"]
        label_idx = self.class_to_idx.get(label_str, 1) # Default to Normal if not found

        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as e:
            # Fallback black image if missing/corrupt
            img = Image.new("RGB", (224, 224), color=(0, 0, 0))

        if self.transform:
            img_tensor = self.transform(img)
        else:
            arr = np.array(img.resize((224, 224)), dtype=np.float32).transpose((2, 0, 1)) / 255.0
            img_tensor = torch.from_numpy(arr)

        return img_tensor, label_idx

def train_model(manifest_path="dataset_manifest.csv",
                epochs=10,
                batch_size=32,
                lr=0.0003,
                output_path="road_defect_cnn.pt",
                device=None):
    
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load manifest
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file {manifest_path} not found. Run generate_manifest.py first.")

    df = pd.read_csv(manifest_path)
    print(f"Loaded manifest with {len(df)} total samples.")
    print("Class distribution:")
    print(df["label"].value_counts().to_dict())

    # Transforms
    train_transform = FastImageTransform(size=(224, 224), is_train=True)
    val_transform = FastImageTransform(size=(224, 224), is_train=False)

    train_ds = RoadDefectDataset(df, split="train", transform=train_transform)
    val_ds = RoadDefectDataset(df, split="val", transform=val_transform)

    print(f"Training set: {len(train_ds)} samples | Validation set: {len(val_ds)} samples")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    # Model
    model = RoadDefectResNet(num_classes=3)
    model = model.to(device)

    # Class weights to balance loss
    class_counts = df[df["split"] == "train"]["label"].value_counts()
    classes = ["Crack", "Normal", "Pothole"]
    total_train = len(train_ds)
    weights = [total_train / (3.0 * max(1, class_counts.get(c, 1))) for c in classes]
    weight_tensor = torch.tensor(weights, dtype=torch.float32).to(device)
    print(f"Class loss weights: {dict(zip(classes, [round(w, 2) for w in weights]))}")

    criterion = nn.CrossEntropyLoss(weight=weight_tensor)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    best_state = None

    print("\n--- Starting Training ---")
    for epoch in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train_count = 0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train_count += images.size(0)

        scheduler.step()
        train_loss = running_loss / max(1, total_train_count)
        train_acc = (correct_train / max(1, total_train_count)) * 100.0

        # Validation
        model.eval()
        val_loss_running = 0.0
        correct_val = 0
        total_val_count = 0
        per_class_correct = {i: 0 for i in range(3)}
        per_class_total = {i: 0 for i in range(3)}

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss_running += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val_count += images.size(0)

                for l, p in zip(labels.cpu().numpy(), preds.cpu().numpy()):
                    per_class_total[l] += 1
                    if l == p:
                        per_class_correct[l] += 1

        val_loss = val_loss_running / max(1, total_val_count)
        val_acc = (correct_val / max(1, total_val_count)) * 100.0
        elapsed = time.time() - t0

        print(f"Epoch {epoch:2d}/{epochs:2d} [{elapsed:.1f}s] - Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")
        
        # Per-class accuracies
        class_acc_str = " | ".join([f"{classes[i]}: {per_class_correct[i]}/{max(1, per_class_total[i])} ({(per_class_correct[i]/max(1, per_class_total[i]))*100:.1f}%)" for i in range(3)])
        print(f"   -> Val Acc by Class: {class_acc_str}")

        if val_acc >= best_val_acc or best_state is None:
            best_val_acc = val_acc
            best_state = model.state_dict().copy()

    # Save best model
    checkpoint = {
        "model_state": best_state if best_state is not None else model.state_dict(),
        "classes": classes,
        "class_to_idx": {c: i for i, c in enumerate(classes)},
        "val_acc": best_val_acc,
        "architecture": "RoadDefectResNet",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    torch.save(checkpoint, output_path)
    print(f"\n[SUCCESS] Best model (Val Acc: {best_val_acc:.2f}%) saved to '{output_path}'")
    return checkpoint

def main():
    parser = argparse.ArgumentParser(description="Train Road Defect ResNet Model")
    parser.add_argument("--manifest", type=str, default="dataset_manifest.csv", help="Path to dataset_manifest.csv")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.0003, help="Learning rate")
    parser.add_argument("--output", type=str, default="road_defect_cnn.pt", help="Output model checkpoint path")
    args = parser.parse_args()

    train_model(
        manifest_path=args.manifest,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        output_path=args.output
    )

if __name__ == "__main__":
    main()
