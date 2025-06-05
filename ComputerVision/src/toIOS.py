from ultralytics import YOLO

# Load a trained YOLO11 PyTorch model
model = YOLO("ComputerVision/runs/detect/train8/weights/best.pt")

# Export the PyTorch model to CoreML INT8 format with NMS layers
# The imgsz property may be adjusted when you export a trained model
model.export(format="coreml", int8=True, nms=True, imgsz=640)