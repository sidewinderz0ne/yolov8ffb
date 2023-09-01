from ultralytics import YOLO

# Load a pretrained YOLOv8n model
model = YOLO('yolov5sTBS.pt')

# Define path to video file
source = 'ch01_00000000324000000.mp4'

# Run inference on the source
model.predict(source, save=False, imgsz=640, conf=0.3, device='0', show=True)