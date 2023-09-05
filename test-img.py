from ultralytics import YOLO

# Load a pretrained YOLOv8n model
model = YOLO('yolov8s.pt')

# Define path to the image file
source = 'ss.jpg'

# Run inference on the source
#results = model(source)  # list of Results objects

model.predict('ss.jpg', save=True, imgsz=640, conf=0.5, device='0', show=True)