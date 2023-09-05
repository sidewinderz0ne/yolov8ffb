from collections import defaultdict

import cv2
import numpy as np

from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("./Models/yolov8-25-8-23-last.pt")

# Open the video file
video_path = "./Sources/ch01_00000000324000000.mp4"
cap = cv2.VideoCapture(video_path)

# Store the track history
track_history = defaultdict(lambda: [])

# Initialize variables for counting
object_count = 0
object_ids_passed = set()

names = list(model.names.values())
class_count = [0] * len(names)


# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.05, iou=0.5, imgsz=1280)

        # Get the boxes and track IDs
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        cls = results[0].boxes.cls.cpu().tolist()

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Calculate the middle y-coordinate of the frame
        middle_y = annotated_frame.shape[0] // 2

        # Draw the horizontal line
        cv2.line(annotated_frame, (0, middle_y), (annotated_frame.shape[1], middle_y), (0, 255, 0), 2)  # Green line

        # Plot the tracks and count objects passing the line
        for box, track_id, cl in zip(boxes, track_ids, cls):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            if len(track) > 10:  # retain 10 tracks for 10 frames
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            # Check if the object's center point has crossed the line
            if y > middle_y and track_id not in object_ids_passed:
                object_ids_passed.add(track_id)
                object_count += 1
                class_count[int(cl)] += 1

        # Display the object count on the frame
        cv2.putText(annotated_frame, f"COUNT: {object_count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        for index, (name, cc) in enumerate(zip(names, class_count)):
            cv2.putText(annotated_frame, f"{name}: {cc}", (20, ((index + 2) * 40)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
