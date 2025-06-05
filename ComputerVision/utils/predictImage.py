import cv2
import os
from ultralytics import YOLO

# --- CONFIG ---
image_path = 'ComputerVision/dataset/images/val/2015-01-07 axamer lizum (4).jpg'          # Path to input image
model_path = 'ComputerVision/runs/detect/train8/weights/best.pt'              # Path to YOLO model
output_path = 'output5.jpg'          # Output image path

# --- LOAD MODEL ---
model = YOLO(model_path)

# --- LOAD IMAGE ---
image = cv2.imread(image_path)
height, width = image.shape[:2]
filename = os.path.splitext(os.path.basename(image_path))[0]

# --- RUN INFERENCE ---
results = model(image)[0]

# --- DRAW PREDICTIONS ---
for box in results.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    cls_id = int(box.cls[0])
    label = results.names[cls_id]
    conf = float(box.conf[0])
    if conf < 0.6:
        continue

    # Draw box
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 4)

    # Draw label
    text = f'{label} ({conf:.2f})'
    cv2.putText(image, text, (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX,
                3, (0, 0, 255), 2, cv2.LINE_AA)

# --- ADD FILENAME IN CORNER ---
cv2.putText(image, f'File: {filename}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
            3, (0, 0, 0), 2, cv2.LINE_AA)

# --- SAVE RESULT ---
cv2.imwrite(output_path, image)
print(f"Saved result to {output_path}")
