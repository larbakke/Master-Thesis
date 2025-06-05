from ultralytics import YOLO
import cv2

# Load your custom YOLO model
model_path = 'ComputerVision/runs/detect/train8/weights/best.pt'
model = YOLO(model_path)

# Open the video file
video_path = 'SkierSurvivesMassiveAval_Cut.mp4'
print(f"Loading video from: {video_path}")
cap = cv2.VideoCapture(video_path)

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# OPTIONAL: Save the output to a new file
save_output = True
output_path = 'labeled_output.mp4'
if save_output:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO prediction
    results = model(frame)

    # Get annotated frame
    annotated_frame = results[0].plot()

    # Show frame in a window (press 'q' to quit)
    cv2.imshow("YOLOv8 Video", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Write frame to output video
    if save_output:
        out.write(annotated_frame)

# Release resources
cap.release()
if save_output:
    out.release()
cv2.destroyAllWindows()

print("Video processing complete.")
