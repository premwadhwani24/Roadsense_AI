import cv2

def load_image(path, size=(64, 64)):
    img = cv2.imread(path)
    if img is None:
        raise Exception(f"Unable to load image: {path}")

    img = cv2.resize(img, size)
    return img
